# Backups

## Backup Synology Disktation Files

Python script that copies Synology Diskstation user and web files to local Mac and Dropbox folder.

### Setup Venv
    backups$ python3 -m venv venv
    backups$ source venv/bin/activate
    (venv) backups$ pip3 install -r requirements.txt

### Run Script

Run script with gitignored `local_settings.py` file to keep sensitive info out of repo.

    (venv) backup_nas_files$ python backup_diskstation.py --settings=settings_local

## Backup Sandbox Files

### Run Script

Run script with gitignored `local_settings.py` file to keep sensitive info out of repo.

    (venv) backups$ python backup_sandbox.py --settings=settings_local

## Edit Crontab
    env EDITOR=vim crontab -e



