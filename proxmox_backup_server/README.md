# Proxmox Backup Server

This agent plugin checks datastores, task summary (of the last day) as well as prune, sync and verify jobs from Proxmox Backup server.

## TODO: Tape backup and restore jobs

Since I do not use tapes anymore the monitoring of

* Tape backup jobs and
* Tape restore jobs

is currently not implemented. I would be happy to implement these features if someone who uses tape backups could assist me required outputs and testing.

## (Manual) Installation

### Server

Install the checkmk extension package on your server.

*Note: Replace \<version\> with the current version (e.g. 2.4.0).*

```bash
# Switch to your checkmk site user (e.g. cmk)
su - cmk

# Download the checkmk extension paackage 
wget https://github.com/mape2k/check_mk_extensions/raw/refs/heads/cmk2.4/proxmox_backup_server/proxmox_backup_server-<version>.mkp -O /tmp/

# Add the package to your checkmk installation and enable it
mkp add /tmp/proxmox_backup_server-<version>.mkp
mkp enable proxmox_backup_server

# List all installed mkp packages to verify the installation
mkp list
```

### Clients

You can deploy the plugin via bakery. If you're using community edition or won't deploy via bakery you can also install it manually.
The plugin should be executed async, adjust the interval (e.g. 1800 seconds) to your needs.

```bash
# Download the plugin script
mkdir /usr/lib/check_mk_agent/plugins/1800
sudo wget https://github.com/mape2k/check_mk_extensions/raw/refs/heads/cmk2.4/proxmox_backup_server/local/share/check_mk/agents/plugins/proxmox_backup_server.py -O /usr/lib/check_mk_agent/plugins/1800/proxmox_backup_server.py
sudo chmod +x /usr/lib/check_mk_agent/plugins/1800/proxmox_backup_server.py
```

The plugin uses proxmox-backup-debug to query the API locally. **The user *root@pam* needs to be enabled!**

## Troubleshooting

If services did not get discovered by checkmk, please check:

1. Did check_mk_agent on your Proxmox Backup Server output contains "**<<<proxmox_backup_server>>>**"?
2. Login as root on your Proxmox Backup Server and run

   ```
   /usr/sbin/proxmox-backup-debug api get /version
   ```
  You should get a result containing release, repoid and version. Otherwhise check the error message.

## Changelog

### 2.4
  * Initial implementation supporting datastores, task summary and sync/prune/verify jobs supporting checkmk 2.4 or newer

### 2.4.1
  * :warning: **New version of the check_mk_agent plugin – replacement required.**
  * Fix issues with unknown values while Garbage collect is running
  * Ignore running jobs in task summary instead of classify them as error
  * Add exception handling for invalid agent output to prevent crashes in checkmk

### 2.4.2
  * Datastore: Ignore levels for Estimated full in Never