# exim mailqueue

The client plugin will check the exim mailqueue (length, size, age).

## Installation Instructions

### Clients
Copy the the check_mk agent plugin from local/share/check_mk/agents/plugins to /usr/lib/check_mk_agent/plugins/ or use bakery for agent integration.

### Server
Install the exim_mailq-x.x.x.mkp package.

## Changelog

### 2.4
  * Migrate to new plugin API v2 for checkmk 2.3 and newer
  * Add bakery
### 2.0
  * Migrate to plugin API v1 for checkmk 2.0 and newer
