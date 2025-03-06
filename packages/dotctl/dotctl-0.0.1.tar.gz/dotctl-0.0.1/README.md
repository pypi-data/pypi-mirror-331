# DotCtl

---

A CLI Tool to Manage KDE Plasma Settings/Configurations.

## Features

- Save Profile: Save existing plasma config/settings.
- Import Profile: Import existing plasma config/settings from .plsv file.
- Export Profile: Export and share existing plasma config/settings to .plsv file.

## Installation

    pip install dotctl

## Cli Guide

#### Save Profile

    dotctl save <profile_name>
    eg: dotctl save MyProfile

Options:

- `-f, --force` Overwrite already saved profiles
- `-c <path>, --config-file <path>` Use external config file
- `-e <env>, --env <env>` Desktop environment (e.g. kde)
- `-p <password>, --password <password>` Sudo Password to authorize restricted data (e.g. /usr/share)
- `--include-global` Include data from global data directory (/usr/share)
- `--include-sddm` Include sddm data/configs directory (/usr/share/sddm, /etc/sddm.conf.d)
- `--sddm-only` Perform operation only on sddm data/configurations (Note: sudo password required)
- `--skip-sudo` Skip all sudo operations

#### Remove Profile

    dotctl remove <profile_name>
    eg: dotctl remove MyProfile

#### List Profile

    dotctl list

#### Apply Profile

    dotctl apply <profile_name>
    eg: dotctl apply MyProfile

Options:

- `-p <password>, --password <password>` Sudo Password to authorize restricted data (e.g. /usr/share)
- `--sddm-only` Apply only sddm (Note: sudo password required)
- `--skip-global` Skip data from global data directory (/usr/share)
- `--skip-sddm` Skip sddm data/configs directory (/usr/share/sddm, /etc/sddm.conf.d)
- `--skip-sudo` Skip all sudo operations

#### Import Profile

    dotctl import <profile_path>
    eg: dotctl import MyProfile.plsv

Options:

- `-p <password>, --password <password>`
  Sudo Password to authorize restricted data (e.g. /usr/share)
- `--config-only` Perform operation only on plasma configs (skip data, e.g. ~/.config)
- `--data-only` Perform operation only on plasma data (skip configs, e.g. ~/.local/share)
- `--sddm-only` Perform operation only on sddm data/configurations (Note: sudo password required)
- `--skip-global` Skip data from global data directory (/usr/share)
- `--skip-sddm` Skip sddm data/configs directory (/usr/share/sddm, /etc/sddm.conf.d)
- `--skip-sudo` Skip all sudo operations

#### Export Profile

    dotctl export <profile_path>
    eg: dotctl export MyProfile.plsv

Options:

- `-p <password>, --password <password>`
  Sudo Password to authorize restricted data (e.g. /usr/share)
- `--config-only` Perform operation only on plasma configs (skip data, e.g. ~/.config)
- `--data-only` Perform operation only on plasma data (skip configs, e.g. ~/.local/share)
- `--sddm-only` Perform operation only on sddm data/configurations (Note: sudo password required)
- `--skip-global` Skip data from global data directory (/usr/share)
- `--skip-sddm` Skip sddm data/configs directory (/usr/share/sddm, /etc/sddm.conf.d)
- `--skip-sudo` Skip all sudo operations

#### Wipe all Profiles

    dotctl wipe

#### Help

    dotctl -h
    dotctl <action> -h
    eg: dotctl import -h

#### Version

    dotctl -v

## Who do I talk to?

- Repo owner or admin
- Other community or team contact
