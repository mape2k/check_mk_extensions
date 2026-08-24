# Gentoo portage

This plugin checks for available updates (including new slots) and unpatched GLSAs using portage python libraries.

## (Manual) Installation

### Server

Install the checkmk extension package on your server.

*Note: Replace \<version\> with the current version (e.g. 2.4.0).*

```bash
# Switch to your checkmk site user (e.g. cmk)
su - cmk

# Download the checkmk extension paackage 
wget https://github.com/mape2k/check_mk_extensions/raw/refs/heads/cmk2.4/gentoo_portage/gentoo_portage-<version>.mkp -O /tmp/

# Add the package to your checkmk installation and enable it
mkp add /tmp/gentoo_portage-<version>.mkp
mkp enable gentoo_portage

# List all installed mkp packages to verify the installation
mkp list
```

### Clients

You can deploy the plugin via bakery. If you're using community edition or won't deploy via bakery you can also install it manually.
The plugin should be executed async, adjust the interval (e.g. 3600 seconds) to your needs.

```bash
# Download the plugin script
mkdir /usr/lib/check_mk_agent/plugins/3600
sudo wget https://github.com/mape2k/check_mk_extensions/raw/refs/heads/cmk2.4/gentoo_portage/local/share/check_mk/agents/plugins/gentoo_portage.py -O /usr/lib/check_mk_agent/plugins/3600/gentoo_portage.py
sudo chmod +x /usr/lib/check_mk_agent/plugins/1800/gentoo_portage.py
```

There are some variables in the plugin script for configuration:

* **BINPKG** - Consider binary packages from PKGDIR and also query the remote binhost *(default: disabled)*
* **SYNC**: Sync portage tree using "emaint --auto sync" *(default: enabled)*
* **GLSA**: Check for unpatched security advisories *(default: enabled)*

## Changelog

### 2.4.0
  * Initial implementation supporting portage sync, updates and GLSA
