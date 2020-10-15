#!/usr/local/bin/ python3

import logging, os, re, shutil, sys
from datetime import datetime
from simple_settings import settings
import subprocess

logging.basicConfig(
    filename='backup_sandbox.log',
    level=logging.DEBUG,
    datefmt="%m-%d-%Y %H:%M:%S",
    format='%(asctime)s %(levelname)-8s %(message)s',
)

OS_BACKUPS_PATH = settings.BACKUPS_DIRECTORY.split("/")[1:]
OS_BACKUPS_PATH[0] = "/{}".format(OS_BACKUPS_PATH[0])

RSYNC_ARGS = (
    "rsync",
    "-av",
    "-e", "ssh",
)
RSYNC_EXCLUDE_ARGS = (
    "--exclude", "*.pyc",
    "--exclude", "__pycache__",
    "--exclude", "venv",
    "--exclude", "virtualenv",
    "--exclude", "virtual_env",
    "--exclude", "venv_py2",
    "--exclude", ".git",
    "--exclude", "node_modules",
)

ERRORS = []

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

    for user in settings.SANDBOX_USERS:

        dir = os.path.join(*OS_BACKUPS_PATH, destination, user)
        if not os.path.exists(dir):
            os.mkdir(dir)

        '''
            backup home directory
        '''
        remote_directory = '~/'
        print('copying directory {}'.format(remote_directory))
        completed_process = subprocess.run([
            *RSYNC_ARGS,
            *RSYNC_EXCLUDE_ARGS,
            "--exclude", ".cache",
            "--exclude", "Python-3.7.3",        # remove after 3.7 upgrade
            "--exclude", "Python-3.7.3.tar.xz", # remove after 3.7 upgrade
            "--exclude", "overwatch",
            "--exclude", "smoketest",           # .git repo
            "--exclude", "travel-scripts",      # .git repo
            "--exclude", "web-tests-accessory", # .git repo
            "{}@{}:{}".format(user, settings.SANDBOX_HOST, remote_directory),
            "{}/{}/{}".format(settings.BACKUPS_DIRECTORY, destination, user),
        ])
        message = "{} rysync completed with code {}".format(remote_directory, completed_process.returncode)
        if completed_process.returncode != 0:
            ERRORS.append( message )
        print(message)

        '''
            backup personal scripts directory
        '''
        completed_process = subprocess.run([
            *RSYNC_ARGS,
            *RSYNC_EXCLUDE_ARGS,
            "{}@{}:~/scripts".format(user, settings.SANDBOX_HOST),
            "{}/{}/{}/scripts".format(settings.BACKUPS_DIRECTORY, destination, user),
        ])
        message = "~/scripts rysync completed with code {}".format(completed_process.returncode)
        if completed_process.returncode != 0:
            ERRORS.append( message )
        print(message)

        '''
            backup travel-scripts local config files

            formerly: scp hadrob@$HOST:~/travel-scripts/travel/viator/settings/local.py ~/Downloads/$DIRECTORY_NAME/travel-scripts/travel/viator/settings
        '''
        completed_process = subprocess.run([
            *RSYNC_ARGS,
            *RSYNC_EXCLUDE_ARGS,
            "--include", "*local*.py",
            "--include", "*/",
            "--exclude", "*",
            "{}@{}:~/travel-scripts".format(user, settings.SANDBOX_HOST),
            "{}/{}/{}".format(settings.BACKUPS_DIRECTORY, destination, user),
        ])

        message = "~/travel-scripts rysync completed with code {}".format(completed_process.returncode)
        if completed_process.returncode != 0:
            ERRORS.append( message )
        print(message)


        '''
            backup travel local config files
        '''
        completed_process = subprocess.run([
            *RSYNC_ARGS,
            *RSYNC_EXCLUDE_ARGS,
            "--include", "*local*.py",
            "--include", "*/",
            "--exclude", "*",
            "{}@{}:/var/www/travel".format(user, settings.SANDBOX_HOST),
            "{}/{}/{}".format(settings.BACKUPS_DIRECTORY, destination, user),
        ])

        message = "/var/www/travel rysync completed with code {}".format(completed_process.returncode)
        if completed_process.returncode != 0:
            ERRORS.append( message )
        print(message)

        '''
            backup travel-dms local config files
        '''
        completed_process = subprocess.run([
            *RSYNC_ARGS,
            *RSYNC_EXCLUDE_ARGS,
            "--include", "*local*.py",
            "--include", "*/",
            "--exclude", "*",
            "{}@{}:/var/www/travel-dms".format(user, settings.SANDBOX_HOST),
            "{}/{}/{}".format(settings.BACKUPS_DIRECTORY, destination, user),
        ])

        message = "/var/www/travel-dms rysync completed with code {}".format(completed_process.returncode)
        if completed_process.returncode != 0:
            ERRORS.append( message )
        print(message)

        '''
            backup poseidon local config files
        '''
        completed_process = subprocess.run([
            *RSYNC_ARGS,
            *RSYNC_EXCLUDE_ARGS,
            "--include", "*local*.py",
            "--include", "*/",
            "--exclude", "*",
            "{}@{}:/var/www/poseidon".format(user, settings.SANDBOX_HOST),
            "{}/{}/{}".format(settings.BACKUPS_DIRECTORY, destination, user),
        ])

        message = "/var/www/poseidon rysync completed with code {}".format(completed_process.returncode)
        if completed_process.returncode != 0:
            ERRORS.append( message )
        print(message)

    print("done")

def delete_local_archive():
    print("removing local archive...")
    shutil.rmtree("{}/archive-sandbox".format(settings.BACKUPS_DIRECTORY))
    print("done")

def run():

    start_date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    print("initializing {} backup to local ({})".format(
        settings.SANDBOX_HOST,
        start_date,
    ))

    try:
        archive_current_backup()
        dir_name = create_new_directory()
        create_new_backup(dir_name)
        delete_local_archive()
    except TypeError as error:
        message = "TypeError: {}".format(error)
        ERRORS.append(message)
    except:
        message = "Unexpected error: {}".format(sys.exc_info()[0])
        ERRORS.append(message)

    # success/error logging
    if len(ERRORS) == 0:
        success_message = "{} backed up to local directory {}".format(
            settings.SANDBOX_HOST,
            dir_name,
        )
        print(success_message)
        logging.info(success_message)
    else:
        error_message = "{} backup encountered the following errors: {}".format(
            settings.SANDBOX_HOST,
            ", ".join(ERRORS),
        )
        print(error_message)
        logging.error(error_message)

    print("finis")

run()