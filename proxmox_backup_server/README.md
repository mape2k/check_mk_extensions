# Proxmox Backup Server

The client plugin will check the Proxmox Backup Server.

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

The plugin uses proxmox-backup-debug to query the API locally.

## Changelog

### 2.4
  * Initial implementation supporting datastores and task summary