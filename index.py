import os
import subprocess
import datetime

# Set variables
DATABASE = 'excelite'
USER = 'root'
PASSWORD = ''
BACKUP_DIR = 'backup'
DATE = datetime.datetime.now().strftime("%Y%m%d%H%M")

# Create backup filename
backup_filename = f"{DATABASE}_backup_{DATE}.sql"

# Dump the database
backup_command = f"/Applications/XAMPP/xamppfiles/bin/mysqldump -u {USER} -p{PASSWORD} {DATABASE} > {os.path.join(BACKUP_DIR, backup_filename)}"

# Run the backup
subprocess.run(backup_command, shell=True)

print(f"Backup {backup_filename} created successfully.")