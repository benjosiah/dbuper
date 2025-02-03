# dbuper

## Introduction
`dbuper` is a database backup tool designed for seamless, automated backups with support for multiple storage options, including local directories, Google Drive, and Dropbox. It provides a straightforward command-line interface for managing backups, scheduling, and configuration, allowing you to set up regular backups and easily retrieve stored backups when needed.

## Prerequisites
To use `dbuper`, ensure you have:
- **Python 3.8+** installed on your system.
- **pip** or **pipx** for installation.
- **Database Client Tools** like `mysqldump` (for MySQL).
- **Cloud SDKs** (if using cloud storage), such as Google Drive API credentials or Dropbox SDK, configured for seamless integration.

## Installation
You can install `dbuper` globally via pip or pipx:

### Using pip (Recommended for Virtual Environments)
```bash
pip install dbuper
```

### Using pipx (Recommended for Global Installation)
```bash
pip install pipx
pipx install dbuper
```
To verify the installation, run:

```bash
dbuper --version
```

## Usage
### Configuration
Set up a database configuration with dbuper by specifying the required connection details. This configuration makes it easier to reuse and manage multiple backup sources.

```bash
dbuper register --name mydatabase --host localhost --user dbuser --password dbpass
```
### List Configurations
View all registered database configurations to confirm your setup:

```bash
dbuper list
```

### Backup
1. Local Backup:

```bash
dbuper backup --config-name mydatabase --local-path /path/to/backup
```
2. Google Drive Backup:

```bash
dbuper backup --config-name mydatabase --cloud gdrive --gdrive-folder-id your_folder_id --gdrive-config-file path_to_gdrive_config.json
```

3. Dropbox Backup:

```bash
dbuper backup --config-name mydatabase --cloud dropbox --dropbox-token your_dropbox_token
```

### Schedule Backups
1. Local Scheduled Backup:

```bash
dbuper schedule:backup --config-name mydatabase --interval 60 --local-path /path/to/backup
```

2. Google Drive Scheduled Backup:

```bash
dbuper schedule:backup --config-name mydatabase --interval 60 --cloud gdrive --gdrive-folder-id your_folder_id --gdrive-config-file path_to_gdrive_config.json
```

3. Dropbox Scheduled Backup:

```bash
dbuper schedule:backup --config-name mydatabase --interval 60 --cloud dropbox --dropbox-token your_dropbox_token
```

### List Schedules
To view all active backup schedules, use:

```bash
dbuper schedule:list
```

### Version
Check the installed version of dbuper:

```bash
dbuper --version
```

This outline provides a concise and clear guide to getting started with `dbuper`, covering all essential commands for setup and use. Let me know if you’d like more details on any section!





