# Backup Synology Diskstation Files

Python script that copies Synology Diskstation user and web files to local Mac and Dropbox folder.

## Setup Venv
    backup_nas_files$ python3 -m venv venv
    backup_nas_files$ source venv/bin/activate
    (venv) backup_nas_files$ pip3 install -r requirements.txt

## Run Script

Run script with gitignored `local_settings.py` file to keep sensitive info out of repo.

    (venv) backup_nas_files$ python backup_diskstation.py --settings=settings_local

## Edit Crontab
    env EDITOR=vim crontab -e



