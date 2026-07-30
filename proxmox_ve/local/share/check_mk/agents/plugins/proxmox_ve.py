#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) 2026 Marcel Pennewiss <opensource@pennewiss.de>

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  This file is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

# This checkmk agent plugin for Proxmox VE runs on the Proxmox VE node
# itself - either via local "pvesh" cli (default) or via the API over
# HTTPS. It produces the same output as the official Promox VE special
# agent including piggyback sections for Virtual Machines and Linux
# Containers (LXC). In most places, it (re)uses the source code of
# the Proxmox VE special agent.

# Version: 1.0

# Config file: $MK_CONFDIR/proxmox_ve.cfg

# Use annotations like python 3.14 or newer
from __future__ import annotations

import itertools
import json
import os
import re
import requests
import requests.auth
import requests.cookies
import shutil
import subprocess
import sys
import tempfile
import tomllib
import urllib3

from collections.abc import Callable, Collection, Iterable, Generator, Mapping, MutableMapping, MutableSequence, Sequence
from contextlib import contextmanager
from dataclasses import asdict, dataclass, is_dataclass, field, fields
from datetime import datetime, timedelta
from enum import Enum, StrEnum
from json import JSONDecodeError
from types import UnionType
from typing import cast, dataclass_transform, get_args, get_type_hints, get_origin, Any, ClassVar, Literal, Union
from zoneinfo import ZoneInfo


@dataclass
class Config:
    """Dataclass for configuration file"""
    host: str = ""
    api_token_id: str = ""
    api_token_secret: str = ""
    username: str = ""
    password: str = ""
    port: int = 8006
    no_cert_check: bool = False
    # Calculated field: Simplification due to compatibility in ProxmoxVeApi
    verify_ssl: bool = True
    timeout: int = 50
    log_cutoff_weeks: int = 2


class CannotRecover(RuntimeError):
    """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py"""
    ...


"""Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py"""
RequestStructure = Sequence[Mapping[str, Any]] | Mapping[str, Any]


@dataclass_transform(field_specifiers=(field,), kw_only_default=True)
class BaseModel:
    """Base Model class implements pydantic behaviour for Dataclass"""

    # Only subclasses are turned into dataclasses (see __init_subclass__).
    # Declaring this satisfies the DataclassInstance protocol for fields()/asdict().
    __dataclass_fields__: ClassVar[dict[str, Any]]

    def __init_subclass__(cls, *, frozen: bool = False, kw_only: bool = True, **kw):
        """Init dataclass like pydantic Model

        defaults:
        frozen = False (pydantic: mutable as default)
        kw_only = True (pydantic: always keyword only)
        """
        super().__init_subclass__(**kw)
        # Make subclass in-place to a dataclass
        dataclass(frozen=frozen, kw_only=kw_only)(cls)

    def __post_init__(self):
        """Check types of values after initialization"""
        hints = get_type_hints(type(self))
        for entry in fields(self):
            expected = hints[entry.name]
            value = getattr(self, entry.name)
            origin = get_origin(expected) or expected

            type_ok = True
            if origin is Literal:
                type_ok = any(value == arg and type(value) is type(arg) for arg in get_args(expected))
            elif origin is UnionType:
                type_ok = isinstance(value, expected)
            elif origin is Union:
                type_ok = isinstance(value, tuple(
                    type(None) if a is None else a for a in get_args(expected)
                ))
            elif origin is not None:
                type_ok = isinstance(value, origin)
            elif isinstance(expected, type):
                type_ok = isinstance(value, expected)
            if not type_ok:
                raise ValueError(f'Expected {entry.name} to be {entry.type}, '
                                 f'got {type(value).__name__} (value: {repr(value)})')

    def model_dump(self) -> dict[str, Any]:
        return asdict(self)

    def model_dump_json(self) -> str:
        return json.dumps(
            self.model_dump(),
            default=self._json_default,
            separators=(",", ":")
        )

    @staticmethod
    def _json_default(o: Any) -> Any:
        if isinstance(o, Enum):
            return o.value
        if hasattr(o, "isoformat"):
            return o.isoformat()
        if is_dataclass(o):
            return {f.name: getattr(o, f.name) for f in fields(o)}
        raise TypeError(f"Not serializable: {type(o).__name__}")


class ItemType(StrEnum):
    """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/ha_manager_status.py"""
    QUORUM = "quorum"
    LRM = "lrm"
    SERVICE = "service"
    MASTER = "master"


class QuorumItem(BaseModel, frozen=True):
    """Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/ha_manager_status.py"""
    id: str
    node: str
    status: str
    type: Literal["quorum"]

    @classmethod
    def model_validate(cls, raw: Mapping[str, Any]) -> "QuorumItem":
        """Replaces validation of literal, converts Proxmox API output to QuorumItem."""
        raw_type = str(raw["type"])
        if raw_type != "quorum":
            raise ValueError(f'type must be "quorum", got {raw_type!r}')
        return cls(
            id=str(raw["id"]),
            node=str(raw["node"]),
            status=str(raw["status"]),
            type=cast(Literal["quorum"], raw_type),
        )


# Original used parameter validate_by_name=True; stdlib dataclasses have no alias support.
class ServiceItem(BaseModel, frozen=True):
    """Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/ha_manager_status.py"""
    node: str
    comment: str | None = None
    sid: str
    state: str
    # Original: raw_type with alias="type" (validate_by_name).
    # stdlib dataclasses have no alias support and the field can't be named
    # "type" (shadowed by the property below), so the API "type" value is
    # mapped to raw_type in model_validate instead.
    raw_type: Literal["service"]
    request_state: str | None = None

    @classmethod
    def model_validate(cls, raw: Mapping[str, Any]) -> "ServiceItem":
        """Replaces validation of literal, converts Proxmox API output to ServiceItem."""
        raw_type = str(raw["type"])
        if raw_type != "service":
            raise ValueError(f'raw_type must be "service", got {raw_type!r}')
        return cls(
            node=str(raw["node"]),
            comment=str(raw["comment"]) if raw.get("comment") is not None else None,
            sid=str(raw["sid"]),
            state=str(raw["state"]),
            raw_type=cast(Literal["service"], raw_type),
            request_state=(
                str(raw["request_state"]) if raw.get("request_state") is not None else None
            ),
        )


class LrmNode(BaseModel):
    """Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/ha_manager_status.py"""
    node: str
    status: str
    timestamp: int
    type: Literal["lrm"]
    # Original used = {}; stdlib dataclasses require default_factory for mutable defaults.
    services: Mapping[str, ServiceItem] = field(default_factory=dict)

    @classmethod
    def model_validate(cls, raw: Mapping[str, Any]) -> "LrmNode":
        """Replaces validation of literal, converts Proxmox API output to LrmNode."""
        raw_type = str(raw["type"])
        if raw_type != "lrm":
            raise ValueError(f'type must be "lrm", got {raw_type!r}')
        return cls(
            node=str(raw["node"]),
            status=str(raw["status"]),
            timestamp=int(raw["timestamp"]),
            type=cast(Literal["lrm"], raw_type),
        )


class MasterNode(BaseModel):
    """Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/ha_manager_status.py"""
    node: str
    type: Literal["master"]
    status: str
    timestamp: int

    @classmethod
    def model_validate(cls, raw: Mapping[str, Any]) -> "MasterNode":
        """Replaces validation of literal, converts Proxmox API output to MasterNode."""
        raw_type = str(raw["type"])
        if raw_type != "master":
            raise ValueError(f'type must be "master", got {raw_type!r}')
        return cls(
            node=str(raw["node"]),
            type=cast(Literal["master"], raw_type),
            status=str(raw["status"]),
            timestamp=int(raw["timestamp"]),
        )


class SectionHaManagerCurrent(BaseModel, frozen=True):
    """Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/ha_manager_status.py"""
    quorum: QuorumItem | None = None
    lrm_nodes: Mapping[str, LrmNode]
    master: MasterNode | None = None

    @classmethod
    def from_json_list(
        cls, raw_data: Sequence[Mapping[str, str | int]]
    ) -> "SectionHaManagerCurrent":
        quorum = None
        lrm_nodes: MutableMapping[str, LrmNode] = {}
        services_by_node: MutableMapping[str, MutableMapping[str, ServiceItem]] = {}
        master = None

        for item in raw_data:
            if (t := item.get("type")) == ItemType.QUORUM:
                quorum = QuorumItem.model_validate(item)
            elif t == ItemType.LRM:
                node = str(item["node"])
                lrm_nodes[node] = LrmNode.model_validate(item)
            elif t == ItemType.SERVICE:
                service = ServiceItem.model_validate(item)
                services_by_node.setdefault(service.node, {})[service.sid] = service
            elif t == ItemType.MASTER:
                master = MasterNode.model_validate(item)

        for node, lrm in lrm_nodes.items():
            lrm.services = services_by_node.get(node, {})

        return cls(quorum=quorum, lrm_nodes=lrm_nodes, master=master)


class SectionNodeAllocation(BaseModel, frozen=True):
    """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/node_allocation.py"""
    allocated_cpu: float | None = None
    node_total_cpu: float | None = None
    allocated_mem: float | None = None
    node_total_mem: float | None = None
    status: str


class SectionNodeAttributes(BaseModel, frozen=True):
    """Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/node_attributes.py"""
    # Original used Field(default=""); plain = "" here.
    # stdlib dataclasses have no Field with validation/alias support.
    cluster: str = ""
    # Original used Field(default=""); plain = "" here.
    # stdlib dataclasses have no Field with validation/alias support.
    node_name: str = ""


class NodeStatus(StrEnum):
    """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/node_info.py"""
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class SubscriptionStatus(StrEnum):
    """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/node_info.py"""
    NEW = "new"
    NOTFOUND = "notfound"
    ACTIVE = "active"
    INVALID = "invalid"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class SubscriptionInfo(BaseModel, frozen=True):
    """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/node_info.py"""
    status: SubscriptionStatus | None = None
    next_due_date: str | None = None


class SectionNodeInfo(BaseModel, frozen=True):
    """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/node_info.py"""
    status: NodeStatus
    lxc: Sequence[str]
    qemu: Sequence[str]
    version: str
    subscription: SubscriptionInfo


class StorageType(StrEnum):
    """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/node_storages.py"""
    BTRFS = "btrfs"
    CEPHFS = "cephfs"
    CIFS = "cifs"
    DIR = "dir"
    ESXI = "esxi"
    ISCSI = "iscsi"
    ISCSIDIRECT = "iscsidirect"
    LVM = "lvm"
    LVMTHIN = "lvmthin"
    NFS = "nfs"
    PBS = "pbs"
    RBD = "rbd"
    ZFS = "zfs"
    ZFSPOOL = "zfspool"


class StorageStatus(StrEnum):
    """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/node_storages.py"""
    AVAILABLE = "available"
    ENABLED = "enabled"
    DISABLED = "disabled"
    INACTIVE = "inactive"
    UNKNOWN = "unknown"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    ACTIVE = "active"


class Storage(BaseModel, frozen=True):
    """Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/node_storages.py"""
    node: str
    disk: float | None = None
    maxdisk: float | None = None
    # Original used Field(validation_alias=AliasChoices(...)); use model_validate() here.
    # stdlib dataclasses have no Field with validation/alias support.
    storage_type: StorageType
    status: StorageStatus | None = None
    # Original used Field(validation_alias=AliasChoices(...)); use model_validate() here.
    # stdlib dataclasses have no Field with validation/alias support.
    name: str

    @classmethod
    def model_validate(cls, raw: Mapping[str, Any]) -> "Storage":
        """Replaces AliasChoices, converts Proxmox API output to Storage."""
        raw_type = raw.get("plugintype", raw.get("storage_type"))
        raw_status = raw.get("status")
        return cls(
            node=raw["node"],
            disk=raw.get("disk"),
            maxdisk=raw.get("maxdisk"),
            storage_type=StorageType(raw_type),
            status=StorageStatus(raw_status) if raw_status is not None else None,
            name=raw.get("storage", raw.get("name")),
        )


class StorageLink(BaseModel, frozen=True):
    """Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/node_storages.py"""
    type: str
    size: str
    vmid: str


class SectionNodeStorages(BaseModel, frozen=True):
    """Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/node_storages.py"""
    node: str
    storages: Sequence[Storage]
    # Original used = {}; stdlib dataclasses require default_factory for mutable defaults.
    storage_links: Mapping[str, Sequence[StorageLink]] = field(default_factory=dict)


class Replication(BaseModel, frozen=True):
    """Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/replication.py"""
    id: str
    source: str
    target: str
    # Original used Field(default=None); plain = None here.
    # stdlib dataclasses have no Field with validation/alias support.
    schedule: str | None = None
    last_sync: int
    last_try: int
    next_sync: int
    duration: float
    # Original used Field(default=None); plain = None here.
    # stdlib dataclasses have no Field with validation/alias support.
    error: str | None = None


class SectionReplication(BaseModel, frozen=True):
    """Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/replication.py"""
    node: str
    # Original used Field(default=None); plain = None here.
    # stdlib dataclasses have no Field with validation/alias support.
    cluster: str | None = None
    replications: Sequence[Replication]
    cluster_has_replications: bool


class LockState(StrEnum):
    """
    Original used Enum; use StrEnum here to allow JSON-serialization of members

    Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/vm_info.py
    """
    BACKUP = "backup"
    CLONE = "clone"
    CREATE = "create"
    MIGRATE = "migrate"
    ROLLBACK = "rollback"
    SNAPSHOT = "snapshot"
    SNAPSHOT_DELETE = "snapshot-delete"
    SUSPENDING = "suspending"
    SUSPENDED = "suspended"


class SectionVMInfo(BaseModel, frozen=True):
    """Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/lib/vm_info.py"""
    vmid: str
    node: str
    status: str
    type: Literal["qemu", "lxc"]
    name: str
    # Original used Field(default=0, ge=0). use model_validate() here
    # stdlib dataclasses have no ge constraint
    uptime: int = 0
    lock: LockState | None = None
    cluster: str | None = None


class _ProxmoxVeSession:
    """
    Session

    Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py
    """

    class HTTPAuth(requests.auth.AuthBase):
        """
        Auth

        Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py
        """

        def __init__(
            self,
            base_url: str,
            credentials: Mapping[str, str],
            timeout: int,
            verify_ssl: bool,
        ) -> None:
            """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py"""

            super().__init__()
            ticket_url = base_url + "api2/json/access/ticket"
            response = (
                requests.post(url=ticket_url, verify=verify_ssl, data=credentials, timeout=timeout)
                .json()
                .get("data")
            )

            if response is None:
                raise CannotRecover(
                    "Couldn't authenticate {!r} @ {!r}".format(
                        credentials.get("username", "no-username"), ticket_url
                    )
                )

            self.pve_auth_cookie = response["ticket"]
            self.csrf_prevention_token = response["CSRFPreventionToken"]

        def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
            """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py"""
            r.headers["CSRFPreventionToken"] = self.csrf_prevention_token
            return r

    def __init__(
        self,
        config: Config
    ) -> None:
        """
        Create Session with authentication using username and password or api token

        Original uses multiple parameters, just use full config dataclass here for simplification

        Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py
        """
        def create_session() -> requests.Session:
            session = requests.Session()

            # Original allows username and password here only
            if config.host and config.api_token_id and config.api_token_secret:
                # Authentication with api token
                session.headers["Authorization"] = f"PVEAPIToken={config.api_token_id}={config.api_token_secret}"
            elif config.host and config.username and config.password:
                # Authentication with username and password
                session.auth = self.HTTPAuth(self._base_url, {"username": config.username, "password": config.password}, config.timeout, config.verify_ssl)
                session.cookies = requests.cookies.cookiejar_from_dict(
                    {"PVEAuthCookie": session.auth.pve_auth_cookie}
                )

            session.headers["Connection"] = "keep-alive"
            session.headers["accept"] = ", ".join(
                (
                    "application/json",
                    "application/x-javascript",
                    "text/javascript",
                    "text/x-javascript",
                    "text/x-json",
                )
            )
            return session

        self._timeout = config.timeout
        self._verify_ssl = config.verify_ssl
        # Disable TLS verification warnings for HTTPS API
        if not self._verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self._base_url = "https://%s:%d/" % (config.host, config.port)
        self._session = create_session()

    def __enter__(self) -> Any:
        """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py"""
        return self

    def __exit__(self, *exc_info: object) -> None:
        """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py"""
        self.close()

    def close(self) -> None:
        """close connection to Proxmox VE endpoint

        Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py
        """
        self._session.close()

    def get_api_element(self, path: str) -> object:
        """do an API GET request

        Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py
        """
        try:
            return self._get_raw("api2/json/" + path)
        except requests.exceptions.ReadTimeout:
            raise CannotRecover(f"Read timeout after {self._timeout}s when trying to GET {path}")
        except requests.exceptions.ConnectionError as exc:
            raise CannotRecover(f"Could not GET element {path} ({exc})") from exc
        except JSONDecodeError as e:
            raise CannotRecover("Couldn't parse API element %r" % path) from e

    def _get_raw(self, sub_url: str) -> object:
        """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py"""
        return (
            self._get_logs_or_tasks_paginated(sub_url)
            if sub_url.endswith(("/log", "/tasks"))
            else self._validate_response(
                self._session.get(
                    url=self._base_url + sub_url,
                    verify=self._verify_ssl,
                    timeout=self._timeout,
                ),
                sub_url,
            )
        )

    def _get_logs_or_tasks_paginated(self, sub_url: str) -> list[object]:
        """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py"""
        url = self._base_url + sub_url
        data: list[object] = []
        start = 0
        page_size = 5000
        while True:
            response_data = self._validate_response(
                self._session.get(
                    url=url,
                    verify=self._verify_ssl,
                    timeout=self._timeout,
                    params={"start": start, "limit": page_size},
                ),
                sub_url,
            )
            assert isinstance(response_data, Sequence)
            data += response_data

            if len(response_data) < page_size:
                break

            start += page_size

        return data

    @staticmethod
    def _validate_response(response: requests.Response, sub_url: str) -> object:
        """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py"""
        if not response.ok:
            return []
        response_json = response.json()
        if "errors" in response_json:
            raise CannotRecover(
                "Could not fetch {!r} ({!r})".format(sub_url, response_json["errors"])
            )
        return response_json.get("data")


class _ProxmoxVeSessionPvesh:
    """
    Session for pvesh

    This class is compatible with _ProxmoxVeSession and use pvesh in get instead of request session.

    Some filters are applied in get functions to prevent unnecessary and time expensive pvesh calls:
    * API Calls returning only a list of subtasks
    * API Calls for Task list (filter vzdump and Log cutoff timestamp)
    """

    PROXMOX_PVESH = "/usr/bin/pvesh"

    def __init__(
        self,
        config: Config
    ) -> None:

        if shutil.which(self.PROXMOX_PVESH) is None:
            raise RuntimeError(f"{self.PROXMOX_PVESH} not found and no HTTPS API configured.")
        self._timeout = config.timeout
        self._log_cutoff_timestamp = int((datetime.now() - timedelta(weeks=config.log_cutoff_weeks)).timestamp())

    def __enter__(self) -> Any:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def close(self) -> None:
        pass

    def get_api_element(self, path: str) -> object:
        """do an API GET request"""
        try:
            return self._get_raw(path)
        except requests.exceptions.ReadTimeout:
            raise CannotRecover(f"Read timeout after {self._timeout}s when trying to GET {path}")
        except requests.exceptions.ConnectionError as exc:
            raise CannotRecover(f"Could not GET element {path} ({exc})") from exc
        except JSONDecodeError as e:
            raise CannotRecover("Couldn't parse API element %r" % path) from e

    def _get_raw(self, sub_url: str) -> object:
        return (
            self._get_logs_or_tasks_paginated(sub_url)
            if sub_url.endswith(("/log", "/tasks"))
            else self._validate_response(
                self.get(
                    url=sub_url
                ),
                sub_url,
            )
        )

    def _get_logs_or_tasks_paginated(self, sub_url: str) -> list[object]:
        data: list[object] = []
        start = 0
        page_size = 5000

        # Filter only vzdump tasks in cutoff days window
        params_filter = {}
        if sub_url.endswith("/tasks"):
            params_filter = {
                "typefilter": "vzdump",
                "since": self._log_cutoff_timestamp
            }

        while True:
            response_data = self._validate_response(
                self.get(
                    url=sub_url,
                    params={"start": start, "limit": page_size} | params_filter,
                ),
                sub_url,
            )
            assert isinstance(response_data, Sequence)
            data += response_data

            if len(response_data) < page_size:
                break

            start += page_size

        return data

    @staticmethod
    def _validate_response(response: str, sub_url: str) -> object:
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON output for API request {sub_url}: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error while executing API request {sub_url}: {e}") from e

    def get(self, url: str, params: dict[str, Any] = {}) -> str:
        """do an API GET request (like requests.Session) pvesh"""

        # Do no break compatibility with get_tree
        # Response API calls which only return a list of subtree names directly
        # with an empty list to save time expensive pvesh calls
        ignore_patterns = re.compile("|".join(
            f"(?:{p})" for p in [
                r"",
                r"cluster",
                r"cluster/ha",
                r"cluster/ha/status",
                r"nodes/[^/]+",
                r"nodes/[^/]+/lxc/\d+",
                r"nodes/[^/]+/qemu/\d+",
                r"nodes/[^/]+/tasks/UPID[^/]+",
            ]
        ))
        if ignore_patterns.fullmatch(url):
            # Return emtpy list as string for validate_response
            return "[]"

        command = [
            self.PROXMOX_PVESH,
            "get",
            f"/{url}",
            "--output-format",
            "json"
        ]

        for param, value in params.items():
            command.append(f"--{param}")
            command.append(str(value))

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=self._timeout,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Command execution failed with exit code "
                f"{e.returncode}: {e.stderr.strip()}"
            ) from e
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Command execution for {url} timed out")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON output: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error while executing API request: {e}") from e


class ProxmoxVeAPI:
    """
    Wrapper for ProxmoxVeSession which provides high level API calls

    Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py
    """

    def __init__(self, config: Config) -> None:
        """
        Original uses multiple parameters, just use full config dataclass here for simplification

        Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py
        """

        try:
            if config.host:
                self._session = _ProxmoxVeSession(config)
            else:
                self._session = _ProxmoxVeSessionPvesh(config)
        except requests.exceptions.ConnectTimeout:
            raise CannotRecover(f"Timeout after {config.timeout}s when trying to connect to {config.host}:{config.port}")
        except requests.exceptions.ConnectionError as exc:
            raise CannotRecover(f"Could not connect to {config.host}:{config.port} ({exc})") from exc

    def __enter__(self) -> Any:
        """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py"""
        self._session.__enter__()
        return self

    def __exit__(self, *exc_info: object) -> None:
        """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py"""
        self._session.__exit__(*exc_info)
        self._session.close()

    def get(self, path: str | Iterable[str]) -> Any:
        """Handle request items in form of 'path/to/item' or ['path', 'to', 'item']

        Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py
        """
        return self._session.get_api_element(
            path if isinstance(path, str) else "/".join(map(str, path))
        )

    def get_tree(self, requested_structure: RequestStructure) -> Any:
        """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libproxmox.py"""
        def rec_get_tree(
            element_name: str | None,
            requested_structure: RequestStructure,
            path: Iterable[str],
        ) -> Any:
            """Recursively fetch data from API to match <requested_structure>"""
            def is_list_of_subtree_names(data: RequestStructure) -> bool:
                """Return True if given data is a list of dicts containing names of subtrees,
                e.g [{'name': 'log'}, {'name': 'options'}, ...]"""
                return bool(data) and all(
                    isinstance(elem, Mapping) and tuple(elem) in {("name",), ("subdir",), ("cmd",)}
                    for elem in data
                )

            def extract_request_subtree(request_tree: RequestStructure) -> RequestStructure:
                """If list if given return first (and only) element return the provided data tree"""
                return (
                    request_tree
                    if isinstance(request_tree, Mapping)
                    else next(iter(request_tree))
                    if len(request_tree) > 0
                    else {}
                )

            def extract_variable(st: RequestStructure) -> Mapping[str, Any] | None:
                """Check if there is exactly one root element with a variable name,
                e.g. '{node}' and return its stripped name"""
                if not isinstance(st, Mapping):
                    return None
                if len(st) != 1 or not next(iter(st)).startswith("{"):
                    # we have either exactly one variable or no variables at all
                    assert len(st) != 1 or all(not e.startswith("{") for e in st)
                    return None
                key, value = next(iter(st.items()))
                assert len(st) == 1 and key.startswith("{")
                return {"name": key.strip("{}"), "subtree": value}

            next_path = list(path) + ([] if element_name is None else [element_name])
            subtree = extract_request_subtree(requested_structure)
            variable = extract_variable(subtree)
            response = self._session.get_api_element("/".join(map(str, next_path)))

            if isinstance(response, Sequence):
                # Handle subtree stubs like [{'name': 'log'}, {'name': 'options'}, ...]
                if is_list_of_subtree_names(response):
                    assert variable is None
                    assert not isinstance(requested_structure, Sequence) and isinstance(
                        subtree, Mapping
                    )
                    assert subtree
                    subdir_names = (
                        (
                            elem[
                                next(
                                    identifier
                                    for identifier in ("name", "subdir", "cmd")
                                    if identifier in elem
                                )
                            ]
                        )
                        for elem in response
                    )
                    return {
                        key: rec_get_tree(key, subtree[key], next_path)
                        for key in subdir_names
                        if key in subtree
                    }

                # Handle case when response is a list of arbitrary datasets
                #  e.g [{'uptime': 12345}, 'id': 'server-1', ...}, ...]"""
                if all(isinstance(elem, Mapping) for elem in response):
                    if variable is None:
                        assert isinstance(subtree, Mapping)
                        return (
                            {key: rec_get_tree(key, subtree[key], next_path) for key in subtree}
                            if isinstance(requested_structure, Mapping)
                            else response
                        )  #

                    assert isinstance(requested_structure, Sequence)
                    return [
                        {
                            **elem,
                            **(
                                rec_get_tree(
                                    elem[variable["name"]],
                                    variable["subtree"],
                                    next_path,
                                )
                                or {}
                            ),
                        }
                        for elem in response
                    ]

            return response

        return rec_get_tree(None, requested_structure, [])


class Backup:
    """
    Fetch, cache and process Backup task logs

    Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libbackups.py
    """

    BackupInfo = MutableMapping[str, Any]
    LogData = Iterable[Mapping[str, Any]]
    TaskInfo = Mapping[str, Any]

    class Storage:
        """Implement a cmk.server_side_programs.v1_unstable.Storage compatible Storage for cache"""

        _cache_dir: str = ""

        def __init__(self) -> None:
            """Initialize storage for cache"""
            self._init_cache_directory()

        def _init_cache_directory(self):
            """Ensure backup cache directory exists (mode 0700, owned by root)"""
            cache_directory = os.path.join(
                os.environ.get("MK_VARDIR", "/var/lib/check_mk_agent"),
                "proxmox_ve",
                "backup_cache",
            )
            try:
                os.makedirs(cache_directory, mode=0o700, exist_ok=True)
                self._cache_dir = cache_directory
            except OSError as e:
                sys.stderr.write(f"Warning: cannot create cache dir {self._cache_dir}: {e}\n")

        def read(self, key: str, default: str = "") -> str:
            """Read cache result"""
            cache_file_path = os.path.join(self._cache_dir, key)

            try:
                with open(cache_file_path, mode="r", encoding="utf-8") as file:
                    return file.read()
            except (OSError, FileNotFoundError):
                return default

        def write(self, key: str, value: str) -> None:
            """Write cached result atomically"""
            cache_file_path = os.path.join(self._cache_dir, key)

            try:
                tmp_fd, tmp_file_path = tempfile.mkstemp(dir=self._cache_dir, prefix=f"{key}.")
                try:
                    with os.fdopen(tmp_fd, mode="w", encoding="utf-8") as tmp_file:
                        tmp_file.write(value)
                    os.replace(tmp_file_path, cache_file_path)
                    os.chmod(cache_file_path, 0o600)
                except Exception:
                    os.unlink(tmp_file_path)
                    raise
            except OSError:
                # cache write failure is non-fatal
                pass

    @staticmethod
    def to_bytes(string: str) -> int:
        """Turn a string containing a byte-size with units like (MiB, ..) into an int
        containing the size in bytes

        >>> to_bytes("123B")
        123
        >>> to_bytes("123 B")
        123
        >>> to_bytes("123")
        123
        >>> to_bytes("123KiB")
        125952
        >>> to_bytes("123 KiB")
        125952
        >>> to_bytes("123KB")
        123000
        >>> to_bytes("123 MiB")
        128974848
        >>> to_bytes("123 GiB")
        132070244352
        >>> to_bytes("123.5 GiB")
        132607115264

        Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libbackups.py
        """
        return round(
            (float(string[:-3]) * (1 << 10)) if string.endswith("KiB") else
            (float(string[:-2]) * (10**3)) if string.endswith("KB") else
            (float(string[:-3]) * (1 << 20)) if string.endswith("MiB") else
            (float(string[:-2]) * (10**6)) if string.endswith("MB") else
            (float(string[:-3]) * (1 << 30)) if string.endswith("GiB") else
            (float(string[:-2]) * (10**9)) if string.endswith("GB") else
            (float(string[:-3]) * (1 << 40)) if string.endswith("TiB") else
            (float(string[:-2]) * (10**12)) if string.endswith("TB") else
            float(string[:-1]) if string.endswith("B") else
            float(string)
        )

    @staticmethod
    def collect_vm_backup_info(backup_tasks: Iterable[BackupTask]) -> Mapping[str, BackupInfo]:
        """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libbackups.py"""
        backup_data: dict[str, __class__.BackupInfo] = {}
        for task in backup_tasks:

            # Look for the latest backup for a given VMID in all backup task logs.
            for vmid, bdata in task.backup_data.items():
                # skip if we have a already newer backup
                if vmid in backup_data and backup_data[vmid]["started_time"] > bdata["started_time"]:
                    continue
                backup_data[vmid] = bdata
        return backup_data

    @staticmethod
    def fetch_backup_data(
        config: Config,
        session: ProxmoxVeAPI,
        nodes: Iterable[Mapping[str, Any]],
    ) -> Mapping[str, BackupInfo]:
        """
        Since the Proxmox API does not provide us with information about past backups we read the
        information we need from log entries created for each backup process

        Original uses:
        * args as parameter; use config here
        * get_tree instead of get

        Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libbackups.py
        """

        # Fetching log files is by far the most time consuming process issued by the ProxmoxVE agent.
        # Since logs have a unique UPID we can safely cache them

        cutoff_date = int((datetime.now() - timedelta(weeks=config.log_cutoff_weeks)).timestamp())
        storage = Backup.Storage()

        with Backup.JsonCachedData(
            storage=storage,
            storage_key="upid.log.cache.json",
            cutoff_condition=lambda _, v: bool(v[0] < cutoff_date),
        ) as cached:

            def fetch_backup_log(task: Backup.TaskInfo, node: str) -> tuple[str, Backup.LogData]:
                """Make a call to session.get_tree() to get a log only if it's not cached
                Note: this is just a closure to make the call below less complicated - it could
                also be part of the generator"""
                # todo: specify type, date in request
                timestamp, logs = cached(
                    task["upid"],
                    lambda t=task, n=node: (
                        t["starttime"],
                        # Original uses `session.get_tree` here, which leads to four
                        # additional requests, including a repeated query for tasks.
                        session.get(["nodes", n, "tasks", t["upid"], "log"])
                    ),
                )
                return timestamp, logs

            # todo: check vmid, typefilter source
            #       https://pve.proxmox.com/pve-docs/api-viewer/#/nodes/{node}/tasks
            return Backup.collect_vm_backup_info(
                Backup.BackupTask(
                    task,
                    backup_log,
                    storage,
                    strict=False,
                    dump_logs=False,
                )
                for node in nodes
                for task in node["tasks"]
                if (task["type"] == "vzdump" and int(task["starttime"]) >= cutoff_date)
                for _timestamp, backup_log in (fetch_backup_log(task, node["node"]),)
            )

    @staticmethod
    @contextmanager
    def JsonCachedData(
        storage: Backup.Storage,
        storage_key: str,
        cutoff_condition: Callable[[str, Any], bool],
    ) -> Generator[Callable[[str, Any], Any]]:
        """Store JSON-serializable data on filesystem and provide it if available

        Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libbackups.py
        """

        cache = json.loads(storage.read(key=storage_key, default="{}") or "{}")

        dirty = False
        # note: this must not be a generator - otherwise we modify a dict while iterating it
        for key in [k for k, data in cache.items() if cutoff_condition(k, data)]:
            dirty = True
            del cache[key]

        def setdefault(key: str, value_fn: Callable[[], Any]) -> Any:
            nonlocal dirty
            if key in cache:
                return cache[key]
            dirty = True
            return cache.setdefault(key, value_fn())

        try:
            yield setdefault
        finally:
            if dirty:
                storage.write(storage_key, json.dumps(cache, indent=2))

    class BackupTask:
        """Handles a bunch of log lines and turns them into a set of data needed from the log

        Ported class BackupTask from packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libbackups.py
        """

        class LogParseError(RuntimeError):
            """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libbackups.py"""
            def __init__(self, line: int, msg: str) -> None:
                super().__init__(msg)
                self.line = line

            def __repr__(self) -> str:
                return "%s(%d, %r)" % (self.__class__.__name__, self.line, super().__str__())

        class LogParseWarning(LogParseError):
            """Less critical version of LogParseError

            Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libbackups.py
            """

        def __init__(
            self,
            task: Backup.TaskInfo,
            logs: Backup.LogData,
            storage: Backup.Storage,
            *,
            strict: bool,
            dump_logs: bool,
            dump_erroneous_logs: bool = True,
        ) -> None:
            """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libbackups.py"""
            self.upid, self.type, self.starttime, self.status = "", "", 0, ""
            self.__dict__.update(task)

            if dump_logs:
                storage.write(f"{task['upid']}.log", "\n".join(line["t"] for line in logs))

            try:
                self.backup_data, errors = self._extract_logs(self._to_lines(logs), strict)
            except self.LogParseError as exc:
                # Note: this way of error handling is not ideal. In case a log file could not be
                #       parsed, all gathered data will be ignored and a error message get's written
                #       to the console.
                #       Crashing on the other hand is also bad since we don't have a way to gracefully
                #       handle unknown log file formats.
                #       An option would be to write error data to each VM being mentioned by the
                #       backup.
                #       I don't handle this issue in this change because further communication is
                #       needed and improving testability is still worth it.
                if strict:
                    raise
                self.backup_data, errors = {}, [(exc.line, str(exc))]

            if errors and dump_erroneous_logs:
                storage.write(
                    f"erroneous-{task['upid']}.log",
                    "\n".join(
                        itertools.chain(
                            (line["t"] for line in logs),
                            ("PARSE-ERROR: %d: %s" % (linenr, text) for linenr, text in errors),
                        )
                    ),
                )

        @staticmethod
        def _to_lines(lines_with_numbers: Backup.LogData) -> Iterable[str]:
            """Extract line data from list of dicts containing redundant line numbers and line data
            >>> list(BackupTask._to_lines([{"n": 1, "t": "line1"}, {"n": 2, "t": "line2"}]))
            ['line1', 'line2']

            Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libbackups.py
            """
            # this has been true all the time and is left here for documentation
            # assert all((int(elem["n"]) - 1 == i) for i, elem in enumerate(lines_with_numbers))
            return (
                line
                for elem in lines_with_numbers
                for line in (elem["t"],)
                if isinstance(line, str) and line.strip()
            )

        def __str__(self) -> str:
            """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libbackups.py"""
            return "BackupTask({!r}, t={!r}, vms={!r})".format(
                self.type,
                datetime.fromtimestamp(self.starttime).strftime("%Y.%m.%d-%H:%M:%S"),
                tuple(self.backup_data.keys()),
            )

        @staticmethod
        def _extract_logs(
            logs: Iterable[str],
            strict: bool
        ) -> tuple[Mapping[str, Backup.BackupInfo], Collection[tuple[int, str]]]:
            """
            Parse vzdump log lines into per-VM backup data dicts.
            Non-strict mode: warnings skip the current VM, errors abort the log.

            Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libbackups.py
            """
            log_line_pattern = {
                key: re.compile(pat, re.IGNORECASE)
                for key, pat in (
                    # not yet used - might be interesting for consistency
                    # ("start_job",      r"^INFO: starting new backup job: vzdump (.*)"),
                    # those for pattern must exist for every VM
                    ("start_vm",       r"^INFO: Starting Backup of VM (\d+).*"),
                    ("started_time",   r"^INFO: Backup started at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"),
                    ("finish_vm",      r"^INFO: Finished Backup of VM (\d+) \((\d{2}:\d{2}:\d{2})\).*"),
                    ("error_vm",       r"^ERROR: Backup of VM (\d+) failed - (.*)$"),
                    ("failed_job",     r"^INFO: Failed at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$"),
                    ("create_archive", r"^INFO: creating(?: vzdump)? archive '(.*)'"),
                    ("bytes_written",  r"^INFO: Total bytes written: (\d+) \(.*, (.*)/s\)"),
                    ("transferred",    r"^INFO: transferred (.*) in <?(\d+) seconds(.*)$"),
                    ("uploaded",       r"^INFO: (.*): had to upload (.*) of (.*) in (.*)s, average speed (.*)/s"),
                    ("archive_size",   r"^INFO: archive file size: (.*)"),
                    ("backuped",       r"^INFO: (.*): had to backup (.*) of (.*) \(compressed (.*)\) in ([\d.]+)[\s]*s.*"),
                )
            }

            required_keys = (
                {"started_time", "total_duration", "bytes_written_bandwidth", "bytes_written_size"},
                {"started_time", "total_duration", "transfer_size", "transfer_time"},
                {"started_time", "total_duration", "upload_amount", "upload_time", "upload_total"},
                {"started_time", "total_duration", "backup_amount", "backup_time", "backup_total"},
                {"started_time", "total_duration", "archive_name", "archive_size"},
            )

            result: dict[str, dict[str, Any]] = {}  # mutable Mapping[str, Mapping[str, Any]]
            current_vmid = ""
            current_dataset: dict[str, Any] = {}  # mutable Mapping[str, Any]
            errors = []

            def extract_tuple(line: str, pattern_name: str, count: int = 1) -> Sequence[str] | None:
                """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libbackups.py"""
                if match := log_line_pattern[pattern_name].match(line):
                    return match.groups()[:count]
                return None

            def extract_single_value(line: str, pattern_name: str) -> str | None:
                """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libbackups.py"""
                if match := extract_tuple(line, pattern_name, 1):
                    return match[0]
                return None

            def duration_from_string(string: str) -> float:
                """Return number of seconds from a string like HH:MM:SS
                >>> duration_from_string("21:43:44")
                78224.0
                >>> duration_from_string("44:00:44")
                158444.0

                Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/libbackups.py
                """
                h, m, s = (int(x) for x in string.split(":"))
                return timedelta(hours=h, minutes=m, seconds=s).total_seconds()

            for linenr, line in enumerate(logs):
                try:
                    if start_vmid := extract_single_value(line, "start_vm"):
                        if current_vmid:
                            # this is a consistency problem - we have to abort parsing this log file
                            raise Backup.BackupTask.LogParseError(
                                linenr,
                                f"Captured start of rocessing VM {start_vmid!r} while VM {current_vmid!r} is still active",
                            )
                        current_vmid = start_vmid
                        current_dataset = {}

                    elif finish_vm := extract_tuple(line, "finish_vm", 2):
                        stop_vmid, duration_str = finish_vm
                        if stop_vmid != current_vmid:
                            # this is a consistency problem - we have to abort parsing this log file
                            raise Backup.BackupTask.LogParseError(
                                linenr,
                                f"Found end of VM {stop_vmid!r} while another VM {current_vmid!r} was active",
                            )
                        current_dataset["total_duration"] = duration_from_string(duration_str)

                        # complain if there are missing keys for any satisfying combination of keys
                        if all(r - set(current_dataset.keys()) for r in required_keys):
                            raise Backup.BackupTask.LogParseWarning(
                                linenr,
                                f"End of VM {current_vmid!r} while still information is missing (we have: {set(current_dataset.keys())!r})",
                            )
                        result[current_vmid] = current_dataset
                        current_vmid, current_dataset = "", {}

                    elif error_vm := extract_tuple(line, "error_vm", 2):
                        error_vmid, error_msg = error_vm
                        if current_vmid and error_vmid != current_vmid:
                            # this is a consistency problem - we have to abort parsing this log file
                            raise Backup.BackupTask.LogParseError(
                                linenr,
                                f"Error for VM {error_vmid!r} while another VM {current_vmid!r} was active",
                            )
                        sys.stderr.write(f"Found error for VM {error_vmid}: {error_msg}\n")
                        result[error_vmid] = {**current_dataset, "error": error_msg}
                        current_vmid, current_dataset = "", {}

                    elif started_time := extract_single_value(line, "started_time"):
                        if not current_vmid:
                            raise Backup.BackupTask.LogParseWarning(
                                linenr,
                                "Found start date while no VM was active",
                            )
                        current_dataset["started_time"] = started_time

                    elif failed_at_time := extract_single_value(line, "failed_job"):
                        # in case a backup job fails we store the time it failed as
                        # 'started_time' in order to be able to sort backup jobs
                        for backup_data in result.values():
                            backup_data.setdefault("started_time", failed_at_time)

                    elif bytes_written := extract_tuple(line, "bytes_written", 2):
                        if not current_vmid:
                            raise Backup.BackupTask.LogParseWarning(
                                linenr, "Found bandwidth information while no VM was active"
                            )
                        current_dataset["bytes_written_size"] = int(bytes_written[0])
                        current_dataset["bytes_written_bandwidth"] = Backup.to_bytes(bytes_written[1])

                    elif transferred := extract_tuple(line, "transferred", 2):
                        transfer_size, transfer_time = transferred
                        if not current_vmid:
                            raise Backup.BackupTask.LogParseWarning(
                                linenr, "Found bandwidth information while no VM was active"
                            )
                        current_dataset["transfer_size"] = Backup.to_bytes(transfer_size)
                        current_dataset["transfer_time"] = int(transfer_time)

                    elif archive_name := extract_single_value(line, "create_archive"):
                        if not current_vmid:
                            raise Backup.BackupTask.LogParseWarning(
                                linenr,
                                "Found archive name without active VM",
                            )
                        current_dataset["archive_name"] = archive_name

                    elif archive_size := extract_single_value(line, "archive_size"):
                        if not current_vmid:
                            raise Backup.BackupTask.LogParseWarning(
                                linenr, "Found archive size information without active VM"
                            )
                        current_dataset["archive_size"] = Backup.to_bytes(archive_size)

                    elif uploaded := extract_tuple(line, "uploaded", 5):
                        _, upload_amount, upload_total, upload_time, _ = uploaded
                        if not current_vmid:
                            raise Backup.BackupTask.LogParseWarning(
                                linenr, "Found upload information while no VM was active"
                            )
                        current_dataset["upload_amount"] = Backup.to_bytes(upload_amount)
                        current_dataset["upload_total"] = Backup.to_bytes(upload_total)
                        current_dataset["upload_time"] = float(upload_time)

                    elif backuped := extract_tuple(line, "backuped", 5):
                        _, backup_amount, backup_total, _, backup_time = backuped
                        if not current_vmid:
                            raise Backup.BackupTask.LogParseWarning(
                                linenr, "Found backup information while no VM was active"
                            )
                        current_dataset["backup_amount"] = Backup.to_bytes(backup_amount)
                        current_dataset["backup_total"] = Backup.to_bytes(backup_total)
                        current_dataset["backup_time"] = float(backup_time)

                except Backup.BackupTask.LogParseWarning as exc:
                    if strict:
                        raise
                    sys.stderr.write(f"Error in log at line {linenr}\n")
                    current_vmid, current_dataset = "", {}
                    errors.append((linenr, str(exc)))

            if current_vmid:
                errors.append((0, f"Log for VMID={current_vmid} not finalized"))

            return result, errors


class AgentProxmoxVe:
    """
    Handle API requests and outputs

    Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/agent_proxmox_ve.py
    """

    @staticmethod
    def load_config() -> Config:
        """Load TOML based config file, fall back to defaults for missing keys."""

        # Configuration file in MK_CONFDIR
        config_file = os.path.join(os.environ.get("MK_CONFDIR", "/etc/check_mk"), "proxmox_ve.cfg")

        # Read configuration file, return default config if missing
        try:
            with open(config_file, "rb") as fh:
                data = tomllib.load(fh)
        except FileNotFoundError:
            return Config()
        except (tomllib.TOMLDecodeError, OSError) as e:
            raise RuntimeError(f"Cannot read config {config_file}: {e}") from e

        # Simplification due to compatibility in ProxmoxVeApi
        data["verify_ssl"] = not data.get("no_cert_check", False)

        # Merge with defaults
        try:
            known_fields = {f.name for f in fields(Config)}
            config = Config(**{k: v for k, v in data.items() if k in known_fields})
        except (TypeError) as e:
            raise RuntimeError(f"Error in config file {config_file}: {e}") from e

        return config

    @staticmethod
    def find_storage_for_vmid(
        all_vms: Mapping[str, Mapping[str, object]],
        vmid: str,
        config: Mapping[str, str],
    ) -> MutableMapping[str, MutableSequence[StorageLink]]:
        """Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/agent_proxmox_ve.py"""
        storage_links: MutableMapping[str, MutableSequence[StorageLink]] = {}

        vm_info = all_vms.get(vmid)
        if vm_info is None:
            return storage_links
        vm_type = vm_info.get("type")
        pattern = ("ide", "scsi", "sata", "virtio") if vm_type == "qemu" else ("mp", "rootfs")

        for key, value in config.items():
            if not key.startswith(pattern):
                continue

            storage_name = value.partition(":")[0]
            size = ""
            for part in value.split(","):
                if part.startswith("size="):
                    size = part[5:]
                    break

            storage_links.setdefault(storage_name, []).append(
                StorageLink(type=key, size=size, vmid=vmid)
            )

        return storage_links

    @staticmethod
    def hostname_matches_node(hostname: str, node_name: str) -> bool:
        """Check if the given hostname refers to the given Proxmox node.

        Matches if the hostname equals the node name exactly or is
        an FQDN starting with the node name (e.g. ``pve1.example.com`` for node ``pve1``).

        Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/agent_proxmox_ve.py
        """
        return hostname == node_name or hostname.startswith(node_name + ".")

    @staticmethod
    def node_piggyback_host(hostname: str, node_name: str, all_node_names: Sequence[str]) -> str:
        """Determine the piggyback header for a Proxmox node.

        Returns ``""`` (empty string = assign to the queried host) when the node
        is identified as the host that was queried.  Otherwise returns the Proxmox
        node name so the data is piggybacked to that host.

        Identification works as follows:

        * If *hostname* (the connection target passed to the agent) matches
        *node_name* exactly or as an FQDN prefix the node is "self".
        * If *hostname* does not match **any** node name (e.g. because an IP
        address or a Checkmk alias was used) **and** there is only a single
        node in the cluster, that node is assumed to be "self".

        Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/agent_proxmox_ve.py
        """
        if __class__.hostname_matches_node(hostname, node_name):
            return ""

        hostname_matches_any = any(__class__.hostname_matches_node(hostname, name) for name in all_node_names)
        if not hostname_matches_any and len(all_node_names) == 1:
            return ""

        return node_name

    @staticmethod
    def agent_proxmox_ve_main(config: Config):
        """
        Fetches and writes selected information formatted as agent output to stdout

        Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/agent_proxmox_ve.py
        """

        with ProxmoxVeAPI(
            config
        ) as session:

            data = session.get_tree(
                {
                    "cluster": {
                        "backup": [],
                        "resources": [],
                        "replication": [],
                        "status": [],
                        "ha": {
                            "status": {
                                "current": [],
                            }
                        },
                    },
                    "nodes": [
                        {
                            "{node}": {
                                "subscription": {},
                                # for now just get basic task data - we'll read the logs later
                                "tasks": [],
                                "qemu": [
                                    {
                                        "{vmid}": {
                                            "snapshot": [],
                                            "config": {},
                                        }
                                    }
                                ],
                                "lxc": [
                                    {
                                        "{vmid}": {
                                            "snapshot": [],
                                            "config": {},
                                        }
                                    }
                                ],
                                "version": {},
                                "time": {},
                                "replication": [],
                            },
                        }
                    ],
                    "version": {},
                }
            )

            logged_backup_data = Backup.fetch_backup_data(config, session, data["nodes"])

        # Convert some datatypes required due to use of dataclass instead of pydantic
        DATATYPE_CONVERTERS = {
            # required by Storage
            "disk": float,
            # required by SectionNodeAllocation
            "maxcpu": float,
            "maxdisk": float,
            "maxmem": float
        }
        for node in data['nodes']:
            # required by SubscriptionInfo
            node["subscription"]["status"] = SubscriptionStatus(node["subscription"]["status"])
            # required by SectionNodeInfo
            node["status"] = NodeStatus(node["status"])
            # required by - see DATATYPE_CONVERTERS
            for key, conv in DATATYPE_CONVERTERS.items():
                if key in node:
                    node[key] = conv(node[key])

        for resource in data["cluster"]["resources"]:
            # required by - see DATATYPE_CONVERTERS
            for key, conv in DATATYPE_CONVERTERS.items():
                if key in resource:
                    resource[key] = conv(resource[key])

        all_vms = {
            str(entry["vmid"]): entry
            for entry in data["cluster"]["resources"]
            if entry["type"] in {"lxc", "qemu"} and entry["status"] not in {"unknown"}
        }

        # Original creates a list of all VMs IDs and scheduled backups for output; not needed here
        # backup_data = { ... }

        node_timezones = {}  # Timezones on nodes can be potentially different
        snapshot_data = {}
        config_lock_data = {}

        replications = {node["node"]: list(node.get("replication", [])) for node in data["nodes"]}
        all_storages = {
            entry["id"]: entry for entry in data["cluster"]["resources"] if entry["type"] == "storage"
        }

        ha_manager_status = SectionHaManagerCurrent.from_json_list(
            data["cluster"]["ha"]["status"]["current"]
        )
        cluster_name = next(
            (item["name"] for item in data["cluster"]["status"] if item.get("type") == "cluster"),
            "",
        )
        node_cluster_mapping = {
            item["name"]: cluster_name
            for item in data["cluster"]["status"]
            if item.get("type") == "node" and item.get("name")
        }

        node_storage: MutableMapping[str, MutableMapping[str, MutableSequence[StorageLink]]] = {}
        for node in data["nodes"]:
            if (timezone := node["time"].get("timezone")) is not None:
                node_timezones[node["node"]] = timezone
            # only lxc and qemu can have snapshots
            for vm in node.get("lxc", []) + node.get("qemu", []):
                snapshot_data[str(vm["vmid"])] = {
                    "snaptimes": [x["snaptime"] for x in vm["snapshot"] if "snaptime" in x],
                }
                config_lock_data[str(vm["vmid"])] = {
                    "lock": vm["config"].get("lock"),
                }

                vm_storage = __class__.find_storage_for_vmid(all_vms, str(vm["vmid"]), vm["config"])
                for storage_name, links in vm_storage.items():
                    node_storage.setdefault(node["node"], {}).setdefault(storage_name, []).extend(links)

        def date_to_utc(naive_string: str, tz: str) -> str:
            """
            Adds timezone information to a date string.
            Returns a timezone-aware string

            Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/agent_proxmox_ve.py
            """
            local_tz = ZoneInfo(tz)
            timezone_unaware = datetime.strptime(naive_string, "%Y-%m-%d %H:%M:%S")
            timezone_aware = timezone_unaware.replace(tzinfo=local_tz)
            return timezone_aware.strftime("%Y-%m-%d %H:%M:%S%z")

        #  overwrite all the start time strings with timezone aware start strings
        for vmid in logged_backup_data:
            try:
                # Happens when the VM has backup data but is not in all_vms
                tz = node_timezones[all_vms[vmid]["node"]]
            except KeyError:
                # get the first value of the first key
                tz = next(iter(node_timezones.values()))
            logged_backup_data[vmid]["started_time"] = date_to_utc(
                logged_backup_data[vmid]["started_time"], tz
            )

        for node in data["nodes"]:
            piggyback_host = AgentProxmoxVe.node_piggyback_host(
                # Original used arg.hostname; hostname here
                config.host, node["node"], [n["node"] for n in data["nodes"]]
            )
            sys.stdout.write(f"<<<<{piggyback_host}>>>>\n")
            for name, content in AgentProxmoxVe._create_node_sections(
                node,
                all_vms,
                node_cluster_mapping,
                replications,
                all_storages,
                node_storage,
                ha_manager_status,
                data,
            ):
                # Original uses json.dumps without default, we need asdict for conversion due to Dataclass instead of pydantic
                sys.stdout.write(f"<<<{name}:sep(0)>>>\n{json.dumps(content, default=asdict)}\n")
            if "uptime" in node:
                sys.stdout.write("<<<uptime>>>\n")
                sys.stdout.write(f"{node['uptime']}\n")
            sys.stdout.write("<<<<>>>>\n")

        for vmid, vm in all_vms.items():
            sys.stdout.write(f"<<<<{vm['name'] or ''}>>>>\n")
            for name, content in AgentProxmoxVe._create_vm_sections(
                vmid,
                vm,
                config_lock_data,
                logged_backup_data,
                snapshot_data,
                node_cluster_mapping,
            ):
                # json.dump requires asdict due to Dataclass instead of pydantic
                sys.stdout.write(f"<<<{name}:sep(0)>>>\n{json.dumps(content, default=asdict)}\n")
            sys.stdout.write("<<<<>>>>\n")

    @staticmethod
    def _create_node_sections(
        node: Any,
        all_vms: Mapping[str, Mapping[str, Any]],
        node_cluster_mapping: Mapping[str, Any],
        replications: Mapping[str, Any],
        all_storages: Mapping[str, Any],
        node_storage: Mapping[str, Mapping[str, Sequence[StorageLink]]],
        ha_manager_status: SectionHaManagerCurrent,
        data: Any,
    ) -> Iterable[tuple[str, object]]:
        """Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/agent_proxmox_ve.py"""

        yield (
            "proxmox_ve_node_info",
            SectionNodeInfo(
                status=node["status"],
                lxc=[str(vmid) for vmid in all_vms if all_vms[vmid]["type"] == "lxc"],
                qemu=[str(vmid) for vmid in all_vms if all_vms[vmid]["type"] == "qemu"],
                version=node["version"].get("version", "n/a"),
                subscription=SubscriptionInfo(
                    status=node["subscription"].get("status"),
                    next_due_date=node["subscription"].get("nextduedate"),
                ),
            ).model_dump(),
        )

        running_vms = [
            vm for vm in all_vms.values() if vm["node"] == node["node"] and vm["status"] == "running"
        ]

        has_maxcpu = "maxcpu" in node
        has_maxmem = "maxmem" in node
        yield (
            "proxmox_ve_node_allocation",
            SectionNodeAllocation(
                status=node["status"],
                node_total_cpu=node["maxcpu"] if has_maxcpu else None,
                allocated_cpu=sum(vm["maxcpu"] for vm in running_vms) if has_maxcpu else None,
                node_total_mem=node["maxmem"] if has_maxmem else None,
                allocated_mem=sum(vm["maxmem"] for vm in running_vms) if has_maxmem else None,
            ).model_dump_json(),
        )

        yield (
            "proxmox_ve_replication",
            SectionReplication(
                node=node["node"],
                cluster=node_cluster_mapping.get(node["node"]),
                replications=[
                    Replication(
                        id=repl["id"],
                        source=repl["source"],
                        target=repl["target"],
                        schedule=repl.get("schedule"),
                        last_sync=repl["last_sync"],
                        last_try=repl["last_try"],
                        next_sync=repl["next_sync"],
                        duration=repl["duration"],
                        error=repl.get("error"),
                    )
                    for repl in replications.get(node["node"], [])
                ],
                cluster_has_replications=bool(data["cluster"]["replication"]),
            ).model_dump_json(),
        )

        yield (
            "proxmox_ve_node_storage",
            SectionNodeStorages(
                node=node["node"],
                storages=[
                    # Original uses storage_data here directly
                    # Dataclasses did not validate in Constructor
                    # Dict from API result needs to be converted explicitly to Storage
                    Storage.model_validate(storage_data)
                    for storage_data in all_storages.values()
                    if storage_data.get("node", "") == node["node"]
                ],
                storage_links=node_storage.get(node["node"], {}),
            ).model_dump(),
        )

        yield (
            "proxmox_ve_node_attributes",
            SectionNodeAttributes(
                cluster=node_cluster_mapping.get(node["node"], ""),
                node_name=node["node"],
            ).model_dump_json(),
        )

        yield "proxmox_ve_ha_manager_status", ha_manager_status.model_dump()
        if "mem" in node and "maxmem" in node:
            yield (
                "proxmox_ve_mem_usage",
                {
                    "mem": node["mem"],
                    "max_mem": node["maxmem"],
                },
            )

    @staticmethod
    def _create_vm_sections(
        vmid: str,
        vm: Any,
        config_lock_data: Mapping[str, Mapping[str, str]],
        logged_backup_data: Mapping[str, object],
        snapshot_data: Mapping[str, object],
        node_cluster_mapping: Mapping[str, object],
    ) -> Iterable[tuple[str, object]]:
        """Ported from Source: packages/cmk-plugins/cmk/plugins/proxmox_ve/special_agent/agent_proxmox_ve.py"""
        lock_str = config_lock_data.get(vmid, {}).get("lock")
        lock_state = LockState(lock_str) if lock_str else None
        yield (
            "proxmox_ve_vm_info",
            # Original used model_dump(mode="json"); not required here, Lockstate is serializable StrEnum
            SectionVMInfo(
                vmid=vmid,
                node=vm["node"],
                type=vm["type"],
                status=vm["status"],
                name=vm["name"],
                uptime=vm["uptime"],
                lock=lock_state,
                cluster=str(node_cluster_mapping[vm["node"]])
                if vm["node"] in node_cluster_mapping
                else None,
            ).model_dump(),
        )
        if vm["type"] != "qemu":
            yield (
                "proxmox_ve_disk_usage",
                {
                    "disk": vm["disk"],
                    "max_disk": vm["maxdisk"],
                },
            )
        yield (
            "proxmox_ve_disk_throughput",
            {
                "disk_read": vm["diskread"],
                "disk_write": vm["diskwrite"],
                "uptime": vm["uptime"],
            },
        )
        yield (
            "proxmox_ve_mem_usage",
            {
                "mem": vm["mem"],
                "max_mem": vm["maxmem"],
            },
        )
        yield (
            "proxmox_ve_network_throughput",
            {
                "net_in": vm["netin"],
                "net_out": vm["netout"],
                "uptime": vm["uptime"],
            },
        )
        yield (
            "proxmox_ve_cpu_util",
            {
                "cpu": vm["cpu"],
                "max_cpu": vm["maxcpu"],
                "uptime": vm["uptime"],
            },
        )
        yield (
            "proxmox_ve_vm_backup_status",
            {
                # todo: info about erroneous backups
                "last_backup": logged_backup_data.get(vmid),
            },
        )
        yield ("proxmox_ve_vm_snapshot_age", snapshot_data.get(vmid))


if __name__ == "__main__":
    try:
        config = AgentProxmoxVe.load_config()
        AgentProxmoxVe.agent_proxmox_ve_main(config)
    except RuntimeError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

    sys.exit(0)
