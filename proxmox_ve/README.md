# Proxmox VE

This agent plugin checks Proxmox VE using the Checkmk-Agent.

It produces the same output as the official Promox VE special agent including piggyback sections for Virtual Machines and Linux Containers (LXC). In most places, it (re)uses the source code of the Proxmox VE special agent.

This solution is intended for cases where the Proxmox VE node is not directly accessible from the Checkmk server.

## (Manual) Installation

### Server

Install the checkmk extension package on your server.

*Note: Replace \<version\> with the current version (e.g. 0.1.0).*

```bash
# Switch to your checkmk site user (e.g. cmk)
su - cmk

# Download the checkmk extension paackage 
wget https://github.com/mape2k/check_mk_extensions/raw/refs/heads/cmk2.4/proxmox_ve/proxmox_ve-<version>.mkp -O /tmp/

# Add the package to your checkmk installation and enable it
mkp add /tmp/proxmox_ve-<version>.mkp
mkp enable proxmox-ve

# List all installed mkp packages to verify the installation
mkp list
```

### Clients

You can deploy the plugin via bakery. If you're using community edition or won't deploy via bakery you can also install it manually.
The plugin could be executed async, adjust the interval (e.g. 1800 seconds) to your needs.

> [!NOTE]
> You should run the plugin async if you use pvesh instead of HTTPS due to time expensive pvesh commands!

#### Execute WITHOUT async option (recommended for HTTPS API only)
```bash
# Download the plugin script
sudo wget https://github.com/mape2k/check_mk_extensions/raw/refs/heads/cmk2.4/proxmox_ve/local/share/check_mk/agents/plugins/proxmox_ve.py -O /usr/lib/check_mk_agent/plugins/proxmox_ve.py
sudo chmod +x /usr/lib/check_mk_agent/plugins/proxmox_ve.py
```

#### Execute with async option (recommended for PVESH)
```bash
# Download the plugin script
mkdir /usr/lib/check_mk_agent/plugins/600
sudo wget https://github.com/mape2k/check_mk_extensions/raw/refs/heads/cmk2.4/proxmox_ve/local/share/check_mk/agents/plugins/proxmox_ve.py -O /usr/lib/check_mk_agent/plugins/600/proxmox_ve.py
sudo chmod +x /usr/lib/check_mk_agent/plugins/600/proxmox_ve.py
```

#### Configuration

If hostname and API token or credentials are not configured, the plugin uses pvesh to query the API locally. **The user *root@pam* must then be enabled!**

```bash
# Download the configuration example
sudo wget https://github.com/mape2k/check_mk_extensions/raw/refs/heads/cmk2.4/proxmox_ve/config/proxmox_ve.example.cfg -O /etc/check_mk/proxmox_ve.cfg
```

proxmox_ve.cfg:
```toml
# Proxmox VE

# Using HTTPS API or pvesh:
# Empty hostname -> Use local pvesh cli (using root@pam)
# Hostname with credentials -> Use HTTPS API
#
# Note: HTTP API mode is significantly faster and recommended for larger setups.

# Host (default: empty)
# host = "localhost"

# Authentication with API Token (preferred, default: empty)
# api_token_id = "user@realm!token-id"
# api_token_secret = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Authentication with User credentials (default: empty)
# username = "user@realm"
# password = "xxxxxxxx"

# Port for HTTPS API (default: 8006)
# port = 8006

# Disable TLS verification for HTTPS API: true, false (default: false)
# no_cert_check = false

# Connection timeout in seconds (default: 50)
# timeout = 50

# Fetch logs N weeks back in time (default: 2)
# log_cutoff_weeks = 2
```

## Troubleshooting

If services did not get discovered by checkmk, please check:

1. Did check_mk_agent on your Proxmox VE Node output contains multiple sections starting with "**<<<proxmox_ve_**"?

2. Using pvesh? Login as root on your Proxmox VE Node and run

   ```
   /usr/bin/pvesh get /version
   ```
   You should get a result containing release, repoid and version. Otherwhise check the error message.

3. Run the agent plugin directly and check error messages.

   ```
   /usr/lib/check_mk_agent/plugins/proxmox_ve.py
   ```

## Changelog

### 0.1.0
  * Initial implementation supporting checkmk 2.4 or newer

## Disclosure

Parts of this project were assisted using Claude Code.