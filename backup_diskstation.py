#!/usr/local/bin/ python3

import logging, os, re, shutil, sys
from datetime import datetime
from simple_settings import settings
import paramiko
import subprocess
from scp import (
    SCPClient,
    SCPException
)
logging.basicConfig(
    filename='backup_diskstation.log',
    level=logging.DEBUG,
    datefmt="%m-%d-%Y %H:%M:%S",
    format='%(asctime)s %(levelname)-8s %(message)s',
)

OS_BACKUPS_PATH = settings.BACKUPS_DIRECTORY.split("/")[1:]
OS_BACKUPS_PATH[0] = "/{}".format(OS_BACKUPS_PATH[0])
OS_DROPBOX_BACKUPS_PATH = settings.DROPBOX_BACKUPS_DIRECTORY.split("/")[1:]
OS_DROPBOX_BACKUPS_PATH[0] = "/{}".format(OS_DROPBOX_BACKUPS_PATH[0])

RSYNC_ARGS = [
    "rsync",
    "-av",
    # "-e", "'ssh {}'".format( ' '.join(SSH_ARGS) ),
    "--timeout", "5000",
]
RSYNC_EXCLUDE_ARGS = (
    "--exclude", "*.pyc",
    "--exclude", "__pycache__",
    "--exclude", "venv",
    "--exclude", "virtualenv",
    "--exclude", "virtual_env",
    "--exclude", ".git",
)

'''
ssh.connect(
            settings.DISKSTATION_HOST,
            port=settings.DISKSTATION_PORT,
            username=user,
            key_filename=settings.SSH_KEY,
            look_for_keys=True,
            timeout=5000,
        )
'''

ERRORS = []

# Define progress callback that prints the current percentage completed for the file
def progress(filename, size, sent):
    sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size)*100) )


def archive_current_backup():
    # print("archiving current backup")
    # create archive folders
    dir = os.path.join(*OS_BACKUPS_PATH, "archive-diskstation")
    if not os.path.exists(dir):
        os.mkdir(dir)

    # move old backup folders into archive
    dirs = next( os.walk(settings.BACKUPS_DIRECTORY))[1]
    for d in dirs:
        if re.match('Backup_Diskstation', d, flags=re.IGNORECASE):
            shutil.move(
                "{}/{}".format(settings.BACKUPS_DIRECTORY, d),
                "{}/archive-diskstation/{}".format(settings.BACKUPS_DIRECTORY, d),
            )
    # print("done")


def archive_current_dropbox_backup():
    # print("archiving current dropbox backup")

    # create archive folders
    dir = os.path.join(*OS_DROPBOX_BACKUPS_PATH, "archive-diskstation")
    if not os.path.exists(dir):
        os.mkdir(dir)

    # move old backup folders into Dropbox archive
    dirs = next( os.walk(settings.DROPBOX_BACKUPS_DIRECTORY))[1]
    for d in dirs:
        if re.match('Backup_Diskstation', d, flags=re.IGNORECASE):
            shutil.move(
                "{}/{}".format(settings.DROPBOX_BACKUPS_DIRECTORY, d),
                "{}/archive-diskstation/{}".format(settings.DROPBOX_BACKUPS_DIRECTORY, d),
            )

    # print("done")

def create_new_directory():
    # print("creating new backup directory...")
    name = "Backup_Diskstation_{}".format(
        datetime.now().strftime("%Y%m%d%H%M%S")
    )
    # local
    dir = os.path.join(*OS_BACKUPS_PATH, name)
    if not os.path.exists(dir):
        os.mkdir(dir)

    # print("done")

    return name

def create_new_backup(destination):



    # print("creating a new backup...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()

    for user in settings.DISKSTATION_USERS:

        dir = os.path.join(*OS_BACKUPS_PATH, destination, user)
        if not os.path.exists(dir):
            os.mkdir(dir)

        SSH_ARGS = " ".join([
            "-p", "'{}'".format(settings.DISKSTATION_PORT),
            "-i", "'{}'".format(settings.SSH_KEY),
            "-l", "'{}'".format(user),
            "-v",
            # "{}@{}".format( user, settings.DISKSTATION_HOST )
        ])
        print( SSH_ARGS )
        # return

        '''
            backup home directory
        '''
        remote_directory = '~/'
        print('copying directory {}'.format(remote_directory))

        print(*RSYNC_ARGS)
        # return

        completed_process = subprocess.run([
            *RSYNC_ARGS,
            "-e", "ssh {}".format( SSH_ARGS ),
            *RSYNC_EXCLUDE_ARGS,
            "--exclude", ".cache",
            "{}@{}:{}".format(user, settings.DISKSTATION_HOST, remote_directory),
            "{}/{}/{}".format(settings.BACKUPS_DIRECTORY, destination, user),
        ])
        message = "{} rysync completed with code {}".format(remote_directory, completed_process.returncode)
        if completed_process.returncode != 0:
            ERRORS.append( message )
        print(message)

        # ssh.connect(
        #     settings.DISKSTATION_HOST,
        #     port=settings.DISKSTATION_PORT,
        #     username=user,
        #     key_filename=settings.SSH_KEY,
        #     look_for_keys=True,
        #     timeout=5000,
        # )

        # # with SCPClient(ssh.get_transport(), progress=progress) as scp:
        # with SCPClient(ssh.get_transport()) as scp:
        #     # user home directory files (.ssh, .bashrc)
        #     scp.get(
        #         "~/.bashrc",
        #         "{}/{}/{}/dotbashrc".format(settings.BACKUPS_DIRECTORY, destination, user),
        #     )
        #     scp.get(
        #         "~/.ssh",
        #         "{}/{}/{}/dotssh".format(settings.BACKUPS_DIRECTORY, destination, user),
        #         recursive=True,
        #     )

        #     if user == settings.DISKSTATION_WEBMASTER:
        #         # Wordpress Hyperbackup
        #         scp.get(
        #             "{}/Wordpress Site.hbk".format(settings.DISKSTATION_WORDPRESS_BACKUP_DIRECTORY),
        #             "{}/{}".format(settings.BACKUPS_DIRECTORY, destination),
        #             recursive=True,
        #         )

        #         # local Django settings file
        #         scp.get(
        #             "{}/bryanhadro_django_project/website/website/config/local.py".format(settings.DISKSTATION_WEB_DIRECTORY),
        #             "{}/{}/bryanhadro_django_project_local.py".format(settings.BACKUPS_DIRECTORY, destination),
        #         )
    # print("done")

def copy_backup_to_dropbox(destination):
    # print("copying backup to dropbox...")
    shutil.copytree(
        src="{}/{}".format(settings.BACKUPS_DIRECTORY, destination),
        dst="{}/{}".format(settings.DROPBOX_BACKUPS_DIRECTORY, destination),
    )
    # print("done")

def delete_local_archive():
    # print("removing local archive...")
    shutil.rmtree("{}/archive-diskstation".format(settings.BACKUPS_DIRECTORY))
    # print("done")

def delete_dropbox_archive():
    # print("removing dropbox archive...")
    shutil.rmtree("{}/archive-diskstation".format(settings.DROPBOX_BACKUPS_DIRECTORY))
    # print("done")

def run():

    # start_date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    # print("initializing {} backup to local ({})".format(
    #     settings.DISKSTATION_HOST,
    #     start_date,
    # ))
    # try:
    archive_current_backup()
    archive_current_dropbox_backup()
    dir_name = create_new_directory()
    create_new_backup(dir_name)
    # copy_backup_to_dropbox(dir_name)

    # end_date = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    # print("completed {} backup to local directory {} ({})".format(
    #     settings.DISKSTATION_HOST,
    #     dir_name,
    #     end_date,
    # ))

    # delete_local_archive()
    # delete_dropbox_archive()

    # except FileNotFoundError as error:
    #     ERRORS.append("FileNotFoundError: {}".format(error))
    # except TypeError as error:
    #     ERRORS.append("TypeError: {}".format(error))
    # except FileExistsError as error:
    #     ERRORS.append("FileExistsError: {}".format(error))
    # except NameError as error:
    #     ERRORS.append("NameError: {}".format(error))
    # except SCPException as error:
    #     ERRORS.append("SCPException: {}".format(error))
    # except:
    #     ERRORS.append("Unexpected error:", sys.exc_info()[0])

    # success/error logging
    if len(ERRORS) == 0:
        success_message = "{} backed up to local directory {}".format(
            settings.DISKSTATION_HOST,
            dir_name,
        )
        # print(success_message)
        logging.info(success_message)
    else:
        error_message = "{} backup encountered the following errors: {}".format(
            settings.DISKSTATION_HOST,
            ", ".join(ERRORS),
        )
        # print(error_message)
        logging.error(error_message)

    # print("finis")

run()