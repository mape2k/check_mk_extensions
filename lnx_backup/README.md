# lnx_backup

check_mk plugin to monitor backups based on rsync, tar or dupl

The agent utility will fetch backup information from output of the
running backup. The agent plugin will output backup information.

## INSTALLATION INSTRUCTIONS

On your check_mk clients:
Install the check_mk agent utility (agents/lnx_backup) to /usr/local/bin (or another suitable location).
Install the check_mk agent plugin (agents/plugins/lnx_backup) to /usr/lib/check_mk/plugins/.

On your check server:
Install the lnx_backup-x.x.mkp package

## USING INSTRUCTIONS

Usage: lnx_backup IDENT TYPE PROGRAM [ARGS...]

Execute PROGRAM as subprocess while getting statistic information about the running backup process from subprocess output and write it to an output file. This file can be monitored using Check_MK. The Check_MK Agent will forward the information of all backup files to the monitoring server. The script outputs STDOUT and STDERR like running without scripts!

IDENT   - Name of the backup
TYPE    - type of PROGRAM output (duply, tar, rsync, refresh, empty)
          "refresh" will just refresh the start/end of backup information
          "empty" will just create backup information with zero values
PROGRAM - Programm to run with arguments to follow

rsync requires "--stats", tar requires "--verbose" as argument to output statistic information or filelist which will be fetched by this script. Any PROGRAM should not be run with quiet option!

### EXAMPLE 1

Old backup command line:

```
tar --create --verbose --file backup.tar /tmp/test
```

Backup command line with lnx_backup named MyBackup using tar

```
/usr/local/bin/lnx_backup MyBackup tar tar --create --verbose --file backup.tar /tmp/test
```

### EXAMPLE 2

If you just want to refresh backup information you can use

```
/usr/local/bin/lnx_backup MyBackup refresh
```

This command adds 24 hours to start and end time of backup information.

### EXAMPLE 3

If you just want to create an empty backup information you can use

```
/usr/local/bin/lnx_backup MyBackup empty
```

This command creates backup information with 1 second backup duration, exit code and all other information with 0.