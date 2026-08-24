#!/usr/bin/env python
# SPDX-License-Identifier: GPL-2.0-only
#
# Check for portage updates and security advisories on Gentoo
#
# (c) 2026 Marcel Pennewiss <opensource@pennewiss.de>
#
# Version: 1.0
# Last-Modified: 2026-08-14
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License. This program
# is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
# License for more details. You should have received a copy of the GNU
# General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA.
#
# Output:
# [sync]
# <tree-epoch> <exit_code> (with -1 = unknown / no sync attempted)
# [updates]
# UPDATE <cat/pkg[:slot]> <old-version> <new-version> <repository>
# NEWSLOT <cat/pkg[:slot]> <old-version> <new-version> <repository>
# [glsa]
# <id> <impact> <cat/pkg[:slot]> <old-version> <fixed-version>

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import email.utils
import functools
from typing import Any, NamedTuple
# for conditional imports see is_gentoo and get_world_packages_without_slot_pin

# Consider binary packages from PKGDIR and also query the remote binhost
BINPKG = False
# Sync portage tree using "emaint --auto sync" (timeout: 600s)
SYNC = True
# Check for unpatched security advisories
GLSA = True


class Candidate(NamedTuple):
    cpv: str
    db: Any
    md: dict[str, str] | None


def is_gentoo() -> bool:
    """Detect Gentoo as distribution; import portage into the module namespace on success."""
    if not os.path.exists("/etc/gentoo-release"):
        return False
    try:
        global portage
        import portage
        import portage.versions
        import portage.eapi
        if GLSA:
            import portage.glsa
    except ImportError:
        return False
    return True


def run_sync() -> int:
    """Sync repositories via emaint without output and honours auto-sync in repos.conf.

    Returns the exit code:
      0 = Sync successful
      1 = Error running emaint
    124 = timeout
    127 = emaint not executable
    """
    emaint = shutil.which("emaint") or "/usr/sbin/emaint"
    try:
        return subprocess.run([emaint, "--auto", "sync"],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL,
                              timeout=600,
                              check=False).returncode
    except subprocess.TimeoutExpired:
        return 124
    except OSError:
        return 127
    except subprocess.SubprocessError:
        return 1


def get_tree_timestamp() -> int:
    """Epoch of the main gentoo repository state from metadata/timestamp.chk.

    Returns -1 if the file is missing or unparsable.
    """
    try:
        repository_path = portage.settings.repositories.mainRepoLocation()  # pyright: ignore[reportAttributeAccessIssue]
        with open(os.path.join(repository_path, "metadata", "timestamp.chk")) as fh:
            return int(email.utils.parsedate_to_datetime(fh.read().strip()).timestamp())
    except Exception:
        return -1


def get_world_packages_without_slot_pin() -> set[str]:
    """Get package names from @world that are not pinned to a slot."""
    try:
        from portage._sets import load_default_config
        cfg = load_default_config(portage.settings, portage.db[portage.root])  # pyright: ignore[reportAttributeAccessIssue]
        return {world_package.cp for world_package in cfg.getSetAtoms("selected") if world_package.slot is None}
    except Exception:
        return set()


def get_main_slot_of_cpv(db: Any, cpv: str) -> str:
    """Main slot of a cpv, subslot stripped."""
    try:
        return (db.aux_get(cpv, ["SLOT"])[0] or "0").split("/")[0]
    except Exception:
        return "0"


def get_metadata_if_visible(settings: Any, db: Any, cpv: str) -> dict[str, str] | None:
    """Return metadata for a cpv, or None if emerge would not consider it.

    Checks EAPI, mask, keywords and license. Required for bindbapi,
    whose match() returns unfiltered results.
    """
    # Get Metadata (USE is required to resolve conditional LICENSE entries)
    keys = ["SLOT", "KEYWORDS", "LICENSE", "repository", "EAPI", "USE"]
    try:
        metadata = dict(zip(keys, db.aux_get(cpv, keys)))
    except Exception:
        return None

    # Check invalid EAPI
    eapi = metadata.get("EAPI")
    if eapi and not portage.eapi.eapi_is_supported(eapi):
        return None

    # Check missing mask, keyword and license
    if (settings._getMaskAtom(cpv, metadata)
            or settings._getMissingKeywords(cpv, metadata)
            or settings._getMissingLicenses(cpv, metadata)):
        return None

    # Return metadata if visible
    return metadata


def is_newer(cpv_new: str, cpv_installed: str) -> int:
    """Compare versions on full CPVs

    Return codes:
    -1: cpv_new is older than cpv_installed
     0: version match
     1: cpv_new is newer than cpv_installed
    """
    r = portage.versions.vercmp(
            portage.versions.cpv_getversion(cpv_new),
            portage.versions.cpv_getversion(cpv_installed)
    )
    return 0 if r is None else r


def get_newest_package(
    settings: Any, portdb: Any, bindb: Any, atom: str
) -> Candidate | None:
    """Highest visible version for an atom, from ebuild and binary trees.

    Returns Candidate or None if nothing matches.
    """
    package_candidates = []

    # Select bestmatch ebuild package
    best = portdb.xmatch("bestmatch-visible", atom)
    if best:
        package_candidates.append(Candidate(best, portdb, None))

    # Find all binary packages (no bestmatch available)
    if bindb is not None:
        for cpv in bindb.match(atom):
            md = get_metadata_if_visible(settings, bindb, cpv)
            if md:
                package_candidates.append(Candidate(cpv, bindb, md))

    # No package found
    if not package_candidates:
        return None

    # Binary packages are listed with every version, ebuild packages
    # only with the newest one. Pick the newest across both trees.
    return max(package_candidates, key=functools.cmp_to_key(lambda a, b: is_newer(a.cpv, b.cpv)))


def format_output(candidate: Candidate, slot: str, cpv_installed: str) -> str:
    """Format one output line for a package candidate."""
    cp = portage.versions.cpv_getkey(candidate.cpv)
    name = cp if slot == "0" else "%s:%s" % (cp, slot)
    if candidate.md:
        repo = candidate.md["repository"]
    else:
        repo = candidate.db.aux_get(candidate.cpv, ["repository"])[0]
    return (f"{name} "
            f"{portage.versions.cpv_getversion(cpv_installed)} "
            f"{portage.versions.cpv_getversion(candidate.cpv)} "
            f"{repo or 'unknown'}")


def get_updates() -> list[str]:
    # Portage settings (from make.conf and /etc/portage/*)
    settings = portage.db[portage.root]["vartree"].settings  # pyright: ignore[reportAttributeAccessIssue]
    # Catalog of installed packages (vartree)
    vardb = portage.db[portage.root]["vartree"].dbapi  # pyright: ignore[reportAttributeAccessIssue]
    # Catalog of available packages (porttree)
    portdb = portage.db[portage.root]["porttree"].dbapi  # pyright: ignore[reportAttributeAccessIssue]

    bindb = None
    if BINPKG:
        # Catalog of available binary packages (must be populated before use)
        bintree = portage.db[portage.root]["bintree"]  # pyright: ignore[reportAttributeAccessIssue]
        bintree.populate(getbinpkgs=True)
        bindb = bintree.dbapi

    # Create slot-separated dict of installed packages
    installed = {}
    for cpv in vardb.cpv_all():
        cp = portage.versions.cpv_getkey(cpv)
        installed.setdefault(cp, {})[get_main_slot_of_cpv(vardb, cpv)] = cpv

    # Get packages from world file
    world_packages_without_slot_pin = get_world_packages_without_slot_pin()

    # Check installed packages for updates
    lines = []
    for cp in sorted(installed):
        slots = installed[cp]

        # Package either absent from @world or slot-pinned
        if cp not in world_packages_without_slot_pin:
            # Check only for updates in the same slot
            for slot in sorted(slots):
                cpv_installed = slots[slot]
                atom = f"{cp}:{slot}"
                candidate = get_newest_package(settings, portdb, bindb, atom)
                if candidate and is_newer(candidate.cpv, cpv_installed) > 0:
                    lines.append(f"UPDATE {format_output(candidate, slot, cpv_installed)}")
            continue

        # Package in @world without a slot
        # Check the highest installed version against all available packages
        else:
            latest_cpv_installed = max(slots.values(), key=functools.cmp_to_key(is_newer))
            candidate = get_newest_package(settings, portdb, bindb, cp)
            # Ignore missing or not newer candidate
            if not candidate or is_newer(candidate.cpv, latest_cpv_installed) <= 0:
                continue
            # Get highest slot of candidate
            slot = get_main_slot_of_cpv(candidate.db, candidate.cpv)
            if slot in slots:
                # Package already installed in same slot as candidate
                lines.append(f"UPDATE {format_output(candidate, slot, latest_cpv_installed)}")
            else:
                # Package not installed in same slot as candidate
                lines.append(f"NEWSLOT {format_output(candidate, slot, latest_cpv_installed)}")
    return lines


def get_glsas() -> list[str]:
    """Open GLSA security advisories affecting installed packages.

    One line per affected package, so a single advisory covering
    several packages yields several lines. Advisories already marked
    as applied (glsa_injected) are skipped.

    The reported version is the lowest one that closes the hole, not
    necessarily the newest available one.
    """
    # Portage settings (from make.conf and /etc/portage/*)
    settings = portage.db[portage.root]["vartree"].settings  # pyright: ignore[reportAttributeAccessIssue]
    # Catalog of installed packages (vartree)
    vardb = portage.db[portage.root]["vartree"].dbapi  # pyright: ignore[reportAttributeAccessIssue]
    # Catalog of available packages (porttree)
    portdb = portage.db[portage.root]["porttree"].dbapi  # pyright: ignore[reportAttributeAccessIssue]

    # Advisories manually marked as handled
    applied = set(portage.glsa.get_applied_glsas(settings))

    lines = []
    for glsa_id in portage.glsa.get_glsa_list(settings):
        if glsa_id in applied:
            # GLSA marked as applied
            continue
        try:
            glsa = portage.glsa.Glsa(glsa_id, settings, vardb, portdb)
            if not glsa.isVulnerable():
                # GLSA not vulnerable on system
                continue

            # getMergeList() lists only packages that are installed and
            # need an upgrade as a unsorted sed.
            for cpv_fixed in sorted(glsa.getMergeList()):
                cp = portage.versions.cpv_getkey(cpv_fixed)
                # Advisories are slot-specific, so compare within the
                # slot of the fixed version only
                slot = get_main_slot_of_cpv(portdb, cpv_fixed)
                name = cp if slot == "0" else f"{cp}:{slot}"

                installed = vardb.match(f"{cp}:{slot}")
                if installed:
                    cpv_installed = max(installed, key=functools.cmp_to_key(is_newer))
                    version_installed = portage.versions.cpv_getversion(cpv_installed)
                else:
                    version_installed = "-"

                lines.append(
                    f"{glsa.nr} {glsa.impact_type} {name} "
                    f"{version_installed} "
                    f"{portage.versions.cpv_getversion(cpv_fixed)}")
        except Exception:
            # A single malformed advisory should not abort the whole check
            continue
    return sorted(lines)


def main() -> int:
    if not is_gentoo():
        return 0

    # Sync portage
    sync_exit_code = -1
    if SYNC:
        sync_exit_code = run_sync()

    print("<<<gentoo_portage>>>")
    print("[sync]")
    print(f"{get_tree_timestamp()} {sync_exit_code}")
    print("[updates]")
    try:
        out = get_updates()
        if out:
            print("\n".join(out))
    except Exception as e:
        # Add errorline on any exception
        message = f"{type(e).__name__}: {e}".replace("\n", " ")[:200]
        print(f"ERROR {message}")

    if GLSA:
        print("[glsa]")
        try:
            out = get_glsas()
            if out:
                print("\n".join(out))
        except Exception as e:
            # Add errorline on any exception
            message = f"{type(e).__name__}: {e}".replace("\n", " ")[:200]
            print(f"ERROR {message}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
