#!/usr/bin/env python
import os
import click
import subprocess
import datetime


@click.group()
def cli():
    """Main entry point for dbuper."""
    pass

@cli.command()
@click.option('--version', '-v', is_flag=True, help="Show version of dbuper")
def version(version):
    if version:
        click.echo("dbuper version 1.0.0")

@cli.command()
@click.option('--db-user', required=True, help="Database user")
# @click.option('--db-password', required=True, help="Database password")
@click.option('--db-name', required=True, help="Database name")
@click.option('--output', required=True, help="Output file path")
def backup(db_user, db_name, output):
    BACKUP_DIR = 'backup'
    DATE = datetime.datetime.now().strftime("%Y%m%d%H%M")

    # Create backup filename
    backup_filename = f"{db_name}_backup_{DATE}.sql"
    """Perform a database backup."""
    backup_cmd = f"/Applications/XAMPP/xamppfiles/bin/mysqldump -u {db_user} -p {db_name} >  {os.path.join(BACKUP_DIR, backup_filename)}"
    
    try:
        subprocess.run(backup_cmd, shell=True, check=True)
        click.echo(f"Backup successful! File saved to {output}")
    except subprocess.CalledProcessError as e:
        click.echo(f"Backup failed: {e}")

if __name__ == '__main__':
    cli()
