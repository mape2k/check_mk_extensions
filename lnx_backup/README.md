# Linux backups

The client plugin will cache the output and check results of linux based backups. 

Supported tools:
* duply
* rsync
* tar

## (Manual) Installation

### Server

Install the checkmk extension package on your server.

*Note: Replace \<version\> with the current version (e.g. 2.4.0).*

```bash
# Switch to your checkmk site user (e.g. cmk)
su - cmk

# Download the checkmk extension paackage 
wget https://github.com/mape2k/check_mk_extensions/raw/refs/heads/cmk2.4/lnx_backup/lnx_backup-<version>.mkp -O /tmp/

# Add the package to your checkmk installation and enable it
mkp add /tmp/lnx_backup-<version>.mkp
mkp enable lnx_backup

# List all installed mkp packages to verify the installation
mkp list
```

### Clients

You can deploy the plugin via bakery. If you're using community edition or won't deploy via bakery you can also install it manually.

```bash
# Download the plugin script
sudo wget https://github.com/mape2k/check_mk_extensions/raw/refs/heads/cmk2.4/lnx_backup/local/share/check_mk/agents/plugins/lnx_backup -O /usr/lib/check_mk_agent/plugins/lnx_backup
sudo chmod +x /usr/lib/check_mk_agent/plugins/lnx_backup

# Download the wrapper script
sudo wget https://github.com/mape2k/check_mk_extensions/raw/refs/heads/cmk2.4/lnx_backup/local/share/check_mk/agents/lnx_backup -O /usr/local/bin/lnx_backup
sudo chmod +x /usr/local/bin/lnx_backup
```

## Usage (Client)

Use lnx_backup as a wrapper for the supported tools:

```bash
/usr/local/binlnx_backup <ident> <type> <cmd> [<args>]
```
with
* **\<ident\>** - Name of the backup (e.g. My_rsync_backup)
* **\<type\>** - Used tool or function (allowed: duply, rsync, tar, refresh, empty)
  * *refresh* - will just refresh the start/end of backup information
  * *empty* - will just create backup information with zero values
* **\<cmd\>** - Program to run (e.g. rsync)
* **\<args\>** - All arguments (e.g. --stats --archive /source /backup)

*rsync requires \"--stats\" as argument to output statistic information which will be fetched by this script. Any CMD should not be run with a quiet option!*

The output of the supported tool is temporarily buffered and evaluated on exit. All output and the exit code continue to be transparently displayed or returned.

The wrapper creates a status file for each ident in the folder /var/lib/check_mk_agent/lnx_backup. All status files will be integrated in check_mk_agent using the plugin in /usr/lib/check_mk_agent/plugins/lnx_backup and discovered as individual services on checkmk.

### Example

If your backup is handled by rsync with the following command line:
```bash
rsync --archive /source /backup
```

Add lnx_backup with parameters as wrapper before rsync command:
```bash
/usr/local/bin/lnx_backup My_rsync_backup rsync rsync --stats --archive /source /backup
```
*(rsync requires \"--stats\" as additional argument)*

## Changelog

### 2.4
  * Migrate to new plugin API v2 for checkmk 2.3 and newer
  * Rules for exit code based on regex match
  * Ignore error messages on directory check in plugin
  * Add bakery
### 2.0
  * Migrate to plugin API v1 for checkmk 2.0 and newer
