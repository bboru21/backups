#!/usr/local/bin/ python3

import os, re, shutil, sys
from datetime import datetime
from simple_settings import settings
import paramiko
from scp import (
    SCPClient,
    SCPException
)

OS_BACKUPS_PATH = settings.BACKUPS_DIRECTORY.split("/")[1:]
OS_BACKUPS_PATH[0] = "/{}".format(OS_BACKUPS_PATH[0])

# Define progress callback that prints the current percentage completed for the file
def progress(filename, size, sent):
    sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size)*100) )

def archive_current_backup():
    print("archiving current backup")
    # create archive folders
    dir = os.path.join(*OS_BACKUPS_PATH, "archive-sandbox")
    if not os.path.exists(dir):
        os.mkdir(dir)

    # move old backup folders into archive
    dirs = next( os.walk(settings.BACKUPS_DIRECTORY))[1]
    for d in dirs:
        if re.match('Backup_Sandbox', d, flags=re.IGNORECASE):
            shutil.move(
                "{}/{}".format(settings.BACKUPS_DIRECTORY, d),
                "{}/archive-sandbox/{}".format(settings.BACKUPS_DIRECTORY, d),
            )
    print("done")

def create_new_directory():
    print("creating new backup directory...")
    name = "Backup_Sandbox_{}".format(
        datetime.now().strftime("%Y%m%d%H%M%S")
    )
    # local
    dir = os.path.join(*OS_BACKUPS_PATH, name)
    if not os.path.exists(dir):
        os.mkdir(dir)

    print("done")
    return name

def create_new_backup(destination):

    print("creating a new backup...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()

    for user in settings.SANDBOX_USERS:

        dir = os.path.join(*OS_BACKUPS_PATH, destination, user)
        if not os.path.exists(dir):
            os.mkdir(dir)

        ssh.connect(
            settings.SANDBOX_HOST,
            port=settings.SANDBOX_PORT,
            username=user,
            key_filename=settings.SSH_KEY,
            look_for_keys=True,
            timeout=5000,
        )

        with SCPClient(ssh.get_transport(), progress=progress) as scp:

            scp.get(
                "~/.bashrc",
                "{}/{}/{}/dotbashrc".format(settings.BACKUPS_DIRECTORY, destination, user),
            )
            scp.get(
                "~/google-chrome-beta_current_amd64.deb",
                "{}/{}/{}/google-chrome-beta_current_amd64.deb".format(settings.BACKUPS_DIRECTORY, destination, user),
            )
            scp.get(
                "~/chromedriver",
                "{}/{}/{}/chromedriver".format(settings.BACKUPS_DIRECTORY, destination, user),
            )
            scp.get(
                "~/.ssh",
                "{}/{}/{}/dotssh".format(settings.BACKUPS_DIRECTORY, destination, user),
                recursive=True,
            )

            # scp.get(
            #     "~/scripts",
            #     "{}/{}/{}/scripts".format(settings.BACKUPS_DIRECTORY, destination, user),
            #     recursive=True,
            # )

    print("done")

def delete_local_archive():
    print("removing local archive...")
    shutil.rmtree("{}/archive-sandbox".format(settings.BACKUPS_DIRECTORY))
    print("done")

def run():

    print("initializing {} backup to local...".format(settings.SANDBOX_HOST))

    try:
        archive_current_backup()
        dir_name = create_new_directory()
        create_new_backup(dir_name)
        print("completed {} backup to local directory {}".format(settings.SANDBOX_HOST, dir_name))
        delete_local_archive()
    except TypeError as error:
        print("TypeError: {}".format(error))
    except:
        print("Unexpected error:", sys.exc_info()[0])

    print("finis")

run()

'''





echo "backing up $HOST_NAME scripts directory..."
rsync -av -e ssh --exclude='*.pyc' --exclude='venv' --exclude='virtualenv' hadrob@$HOST:~/scripts ~/Downloads/$DIRECTORY_NAME

echo "backing up $HOST_NAME smoketest repo..."
rsync -av -e ssh --exclude='*.pyc' --exclude='venv' --exclude='virtualenv' hadrob@$HOST:~/smoketest ~/Downloads/$DIRECTORY_NAME

echo "backing up $HOST_NAME travel-scripts repo local settings..."
mkdir ~/Downloads/$DIRECTORY_NAME/travel-scripts
mkdir ~/Downloads/$DIRECTORY_NAME/travel-scripts/travel
mkdir ~/Downloads/$DIRECTORY_NAME/travel-scripts/travel/viator
mkdir ~/Downloads/$DIRECTORY_NAME/travel-scripts/travel/viator/settings
scp hadrob@$HOST:~/travel-scripts/travel/viator/settings/local.py ~/Downloads/$DIRECTORY_NAME/travel-scripts/travel/viator/settings

echo "backing up $HOST_NAME Travel repo local settings..."
mkdir ~/Downloads/$DIRECTORY_NAME/travel
mkdir ~/Downloads/$DIRECTORY_NAME/travel/config
scp hadrob@$HOST:/var/www/travel/config/local.py ~/Downloads/$DIRECTORY_NAME/travel/config

echo "backing up $HOST_NAME Travel DMS repo local settings..."
mkdir ~/Downloads/$DIRECTORY_NAME/travel-dms
mkdir ~/Downloads/$DIRECTORY_NAME/travel-dms/dms
mkdir ~/Downloads/$DIRECTORY_NAME/travel-dms/dms/settings
scp hadrob@$HOST:/var/www/travel-dms/dms/settings/local_settings.py ~/Downloads/$DIRECTORY_NAME/travel-dms/dms/settings
scp hadrob@$HOST:/var/www/travel-dms/dms/settings/local_settings_stag.py ~/Downloads/$DIRECTORY_NAME/travel-dms/dms/settings

echo "$HOST files backed up to ~/Downloads/$DIRECTORY_NAME"

'''