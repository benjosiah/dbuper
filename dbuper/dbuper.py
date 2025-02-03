import os
import click
import json
import subprocess
import time
import dropbox
import boto3
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from datetime import datetime
from crontab import CronTab
import shutil
from . import __version__

DB_CONFIG_FILE = 'db_configs.json'

try:
    from . import __version__
    print("Version:", __version__)
except ImportError as e:
    print("Import error:", e)

# Default backup directory
DEFAULT_BACKUP_PATH = os.path.abspath("backup/")

def load_db_configs():
    """Load existing database configurations from file."""
    if os.path.exists(DB_CONFIG_FILE):
        with open(DB_CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_db_configs(configs):
    """Save database configurations to file."""
    with open(DB_CONFIG_FILE, 'w') as f:
        json.dump(configs, f, indent=4)

# Main CLI entry
@click.group()
@click.version_option(__version__, "--version", help="Show the version of dbuper.")
def cli():
    """Main entry point for dbuper."""
    pass

# Command to show the default backup path
@cli.command()
def path():
    """Show the full path of the backup folder."""
    click.echo(f"Default backup path is: {DEFAULT_BACKUP_PATH}")

# Step 1: Register a New Database Configuration
@cli.command(name='register')
@click.option('--name', prompt="Configuration name", help="Unique name for the database configuration")
@click.option('--db-user', prompt="Database user", help="Database user")
@click.option('--db-password', default='', hide_input=True, help="Database password")
@click.option('--db-name', prompt="Database name", help="Database name")
def register_db(name, db_user, db_password, db_name):
    """Register a new database configuration."""
    configs = load_db_configs()
    if name in configs:
        click.echo(f"Error: A database configuration with the name '{name}' already exists.")
        return

    configs[name] = {
        'user': db_user,
        'password': db_password,
        'database': db_name
    }
    save_db_configs(configs)
    click.echo(f"Database configuration '{name}' registered successfully.")

# Step 2: List All Registered Database Configurations
@cli.command(name='list')
def list_dbs():
    """List all registered databases."""
    configs = load_db_configs()
    if not configs:
        click.echo("No database configurations registered.")
    else:
        click.echo("Registered database configurations:")
        for name in configs:
            click.echo(f"- {name}")

# Step 3: Backup Command with Cloud Options or Local Path
@cli.command()
@click.option('--config-name', prompt="Configuration name", help="Name of the database configuration to use")
@click.option('--cloud', default="local", type=click.Choice(['s3', 'dropbox', 'gdrive', 'local'], case_sensitive=False), 
              prompt="Where to store the backup (s3, dropbox, gdrive, local)", 
              help="Specify cloud storage or local")
@click.option('--local-path', default='backup', help="Local directory path for backup (if applicable)")
@click.option('--s3-bucket', default='', help="Bucket name for S3 storage (if applicable)")
@click.option('--dropbox-token', default='', help="Dropbox access token (if applicable)")
@click.option('--gdrive-folder-id', default='', help="Folder ID for Google Drive (if applicable)")
@click.option('--gdrive-config-file', default='', help="Google Oauth credentials file")
@click.option('--s3-access-key', default='', help="AWS Access Key (if using S3)")
@click.option('--s3-secret-key', default='', help="AWS Secret Key (if using S3)")
def backup(config_name, cloud, local_path, s3_bucket, dropbox_token, gdrive_folder_id, gdrive_config_file, s3_access_key, s3_secret_key):
    """Perform a database backup and upload to specified cloud storage or local."""
    configs = load_db_configs()
    mysqldump_path = shutil.which("mysqldump")
    click.echo(f"{mysqldump_path}")
    if config_name not in configs:
        click.echo(f"Error: No database configuration found with the name '{config_name}'.")
        return

    if mysqldump_path is None:
        click.echo(f"Error: {mysqldump_path} is not installed or not found in the system PATH.")
        return




    # Load the selected database config
    db_config = configs[config_name]
    db_user = db_config['user']
    db_password = db_config['password']
    db_name = db_config['database']

    # Create a backup file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{db_name}_backup_{timestamp}.sql"
    backup_cmd = f"{mysqldump_path} -u {db_user} -p{db_password} {db_name} > {output_file}"

    try:
        subprocess.run(backup_cmd, shell=True, check=True)
        click.echo(f"Backup successful! File saved as {output_file}")

        # Upload to the specified cloud storage or local path
        if cloud == 's3':
            upload_to_s3(output_file, s3_bucket, s3_access_key, s3_secret_key)
        elif cloud == 'dropbox':
            upload_to_dropbox(output_file, dropbox_token)
        elif cloud == 'gdrive':
            upload_to_gdrive(output_file, gdrive_config_file, gdrive_folder_id)
        elif cloud == 'local':
            if not local_path:
                click.echo("Error: You must specify a local directory path.")
            else:
                local_backup(output_file, local_path)

    except subprocess.CalledProcessError as e:
        click.echo(f"Backup failed: {e}")

# Step 4: Schedule a Backup Command
@cli.command(name="schedule:backup")
@click.option('--interval', required=True, type=int, help="Interval in minutes between backups.", prompt="Schedule intervals in minutes")
@click.option('--config-name', prompt="Configuration name", help="Name of the database configuration to use")
@click.option('--cloud', default="local", type=click.Choice(['s3', 'dropbox', 'gdrive', 'local'], case_sensitive=False), 
              prompt="Where to store the backup (s3, dropbox, gdrive, local)", 
              help="Specify cloud storage or local")
@click.option('--local-path', default='backup', help="Local directory path for backup (if applicable)")
@click.option('--s3-bucket', default='', help="Bucket name for S3 storage (if applicable)")
@click.option('--dropbox-token', default='', help="Dropbox access token (if applicable)")
@click.option('--gdrive-folder-id', default='', help="Folder ID for Google Drive (if applicable)")
@click.option('--gdrive-config-file', default='', help="Google Oauth credentials file")
@click.option('--s3-access-key', default='', help="AWS Access Key (if using S3)")
@click.option('--s3-secret-key', default='', help="AWS Secret Key (if using S3)")
def schedule_backup(interval, config_name, cloud, local_path, s3_bucket, dropbox_token, gdrive_folder_id, gdrive_config_file, s3_access_key, s3_secret_key):
    """Schedule a Backup Command"""
    configs = load_db_configs()
    dbuper_path = shutil.which("dbuper")

    if config_name not in configs:
        click.echo(f"Error: No database configuration found with the name '{config_name}'.")
        return
    
    if dbuper_path is None:
        click.echo("Error: dbuper is not installed or not found in the system PATH.")
        return
    
    log_file_path = "dbuper_backup.log"

    script_path = "dbuper_backup.sh"

    # Create the shell script content
    script_content = f"""#!/bin/bash
    echo "$(date +"%Y-%m-%d %H:%M:%S") Running dbuper backup" >> {log_file_path}
    {dbuper_path} backup --config-name={config_name} --cloud={cloud} \\
    {"--local-path=" + local_path if cloud == "local" else ""} \\
    {"--s3-bucket=" + s3_bucket if cloud == "s3" else ""} \\
    {"--dropbox-token=" + dropbox_token if cloud == "dropbox" else ""} \\
    {"--gdrive-folder-id=" + gdrive_folder_id if cloud == "gdrive" else ""} \\
    {"--gdrive-config-file=" + gdrive_config_file if cloud == "gdrive" else ""} \\
    {"--s3-access-key=" + s3_access_key if cloud == "s3" else ""} \\
    {"--s3-secret-key=" + s3_secret_key if cloud == "s3" else ""} \\
    2> >(while read line; do echo "$(date +"%Y-%m-%d %H:%M:%S") ERROR: $line"; done >> {log_file_path}) \\
    >> {log_file_path}

    echo "$(date +"%Y-%m-%d %H:%M:%S") Backup job completed" >> {log_file_path}
    """

    # Write the script to a file
    with open(script_path, "w") as script_file:
        script_file.write(script_content)

    # Make the script executable
    os.chmod(script_path, 0o755)

    # Set up the cron job
    cron = CronTab(user=True)
    job = cron.new(command=f"/bin/bash {script_path}", comment="dbuper_backup")

    job.minute.every(interval)
    cron.write()
    click.echo(f"Scheduled backup every {interval} minutes for database {config_name}.")

# Step 5: List Scheduled Backups
@cli.command(name="schedule:list")
def list_schedules():
    """List Scheduled Backups"""
    cron = CronTab(user=True)
    jobs = list(cron)
    if not jobs:
        click.echo("No schedules found.")
    else:
        for i, job in enumerate(jobs, 1):
            click.echo(f"{i}: {job}")

# Step 6: Delete a Scheduled Backup
@cli.command(name="schedule:delete")
@click.argument('job_index', type=int)
def delete_schedule(job_index):
    """Delete a Scheduled Backup"""
    cron = CronTab(user=True)
    jobs = list(cron)
    if 0 < job_index <= len(jobs):
        cron.remove(jobs[job_index - 1])
        cron.write()
        click.echo(f"Deleted schedule {job_index}.")
    else:
        click.echo("Invalid schedule index.")

# Step 4: Upload to Local Path
def local_backup(file_path, local_directory="backup"):
    """Save the backup file to the specified local directory."""
    try:
        if not os.path.exists(local_directory):
            os.makedirs(local_directory)
        destination = os.path.join(local_directory, os.path.basename(file_path))
        os.rename(file_path, destination)
        click.echo(f"Backup saved locally at: {destination}")
    except Exception as e:
        click.echo(f"Error saving backup locally: {e}")

# Step 5: Upload to Amazon S3
def upload_to_s3(file_path, bucket_name, access_key, secret_key):
    """Upload backup to S3."""
    if not bucket_name or not access_key or not secret_key:
        click.echo("Error: S3 bucket name and credentials are required.")
        return

    s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    try:
        s3.upload_file(file_path, bucket_name, os.path.basename(file_path))
        click.echo(f"Backup uploaded to S3 bucket '{bucket_name}'.")
    except Exception as e:
        click.echo(f"Error uploading to S3: {e}")

# Step 6: Upload to Dropbox
def upload_to_dropbox(file_path, access_token):
    """Upload backup to Dropbox."""
    if not access_token:
        click.echo("Error: Dropbox access token is required.")
        return

    dbx = dropbox.Dropbox(access_token)
    with open(file_path, 'rb') as f:
        try:
            dbx.files_upload(f.read(), f'/{os.path.basename(file_path)}')
            click.echo("Backup uploaded to Dropbox.")
        except Exception as e:
            click.echo(f"Error uploading to Dropbox: {e}")

# Step 7: Upload to Google Drive
def upload_to_gdrive(file_path, gdrive_config_file, folder_id):
    """Upload backup to Google Drive."""
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile(gdrive_config_file)  # Creates local webserver and automatically handles authentication
    gauth.LocalWebserverAuth() 
    drive = GoogleDrive(gauth)

    file_metadata = {'title': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [{'id': folder_id}]

    gfile = drive.CreateFile(file_metadata)
    gfile.SetContentFile(file_path)
    try:
        gfile.Upload()
        click.echo("Backup uploaded to Google Drive.")
    except Exception as e:
        click.echo(f"Error uploading to Google Drive: {e}")

if __name__ == '__main__':
    cli()