#!/usr/local/bin/ python3

from pathlib import Path
import os, re, shutil, sys
from datetime import datetime
from simple_settings import settings
import paramiko
from scp import (
    SCPClient,
    SCPException
)
from common import get_logger

logger = get_logger('backup_droplet1.log')


OS_BACKUPS_PATH = settings.BACKUPS_DIRECTORY.split("/")[1:]
OS_BACKUPS_PATH[0] = "/{}".format(OS_BACKUPS_PATH[0])
OS_DROPBOX_BACKUPS_PATH = settings.DROPBOX_BACKUPS_DIRECTORY.split("/")[1:]
OS_DROPBOX_BACKUPS_PATH[0] = "/{}".format(OS_DROPBOX_BACKUPS_PATH[0])

# Define progress callback that prints the current percentage completed for the file
def progress(filename, size, sent):
    sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size)*100) )


def archive_current_backup():
    # print("archiving current backup")
    # create archive folders
    dir = os.path.join(*OS_BACKUPS_PATH, "archive-droplet1")
    if not os.path.exists(dir):
        os.mkdir(dir)

    # move old backup folders into archive
    for path in Path(settings.BACKUPS_DIRECTORY).glob('Backup_Droplet1*'):
        logger.debug(f'beginning archive of path {path}, exists values is {path.exists()}')
        directory_name = path.name
        shutil.move(
            f"{settings.BACKUPS_DIRECTORY}/{directory_name}",
            f"{settings.BACKUPS_DIRECTORY}/archive-droplet1/{directory_name}",
        )
        logger.debug(f'archive of path {path} complete, exists values is {path.exists()}')
    logger.debug('archived current backup')


def archive_current_dropbox_backup():
    logger.debug("archiving current dropbox backup")

    # create archive folders
    dir = os.path.join(*OS_DROPBOX_BACKUPS_PATH, "archive-droplet1")
    if not os.path.exists(dir):
        os.mkdir(dir)

    # move old backup folders into Dropbox archive
    for path in Path(settings.DROPBOX_BACKUPS_DIRECTORY).glob('Backup_Droplet1*'):
        logger.debug(f'beginning archive of dropbox path {path}, exists values is {path.exists()}')
        directory_name = path.name
        shutil.move(
            f'{settings.DROPBOX_BACKUPS_DIRECTORY}/{directory_name}',
            f'{settings.DROPBOX_BACKUPS_DIRECTORY}/archive-droplet1/{directory_name}',
        )
        logger.debug(f'archive of dropbox path {path} complete, exists values is {path.exists()}')

    logger.debug("archived current dropbox backup")

def create_new_directory():
    logger.debug("creating new backup directory...")
    name = "Backup_Droplet1_{}".format(
        datetime.now().strftime("%Y%m%d%H%M%S")
    )
    # local
    dir = os.path.join(*OS_BACKUPS_PATH, name)
    if not os.path.exists(dir):
        os.mkdir(dir)

    logger.debug("created new backup directory")

    return name

def create_new_backup(destination):
    # print("creating a new backup...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()

    for user in settings.DROPLET1_USERS:

        dir = os.path.join(*OS_BACKUPS_PATH, destination, user)
        if not os.path.exists(dir):
            os.mkdir(dir)

        ssh.connect(
            settings.DROPLET1_HOST,
            port=settings.DROPLET1_PORT,
            username=user,
            key_filename=settings.SSH_KEY,
            look_for_keys=True,
            timeout=5000,
        )

        # with SCPClient(ssh.get_transport(), progress=progress) as scp:
        with SCPClient(ssh.get_transport()) as scp:
            # user home directory files (.ssh, .bashrc)
            scp.get(
                "~/.bashrc",
                "{}/{}/{}/dotbashrc".format(settings.BACKUPS_DIRECTORY, destination, user),
            )
            # scp.get(
            #     "~/.bash_profile",
            #     "{}/{}/{}/dotbash_profile".format(settings.BACKUPS_DIRECTORY, destination, user),
            # )
            scp.get(
                "~/.ssh",
                "{}/{}/{}/dotssh".format(settings.BACKUPS_DIRECTORY, destination, user),
                recursive=True,
            )

            if user == settings.DROPLET1_WEBMASTER:
                # local and prod Django settings files
                scp.get(
                    "{}/bryanhadro/website/settings/local.py".format(settings.DROPLET1_WEB_DIRECTORY),
                    "{}/{}/bryanhadro_local.py".format(settings.BACKUPS_DIRECTORY, destination),
                )
                scp.get(
                    "{}/bryanhadro/website/settings/prod.py".format(settings.DROPLET1_WEB_DIRECTORY),
                    "{}/{}/bryanhadro_prod.py".format(settings.BACKUPS_DIRECTORY, destination),
                )
                scp.get(
                    "{}/bryanhadro/website/db.sqlite3".format(settings.DROPLET1_WEB_DIRECTORY),
                    "{}/{}/bryanhadro_db.sqlite3".format(settings.BACKUPS_DIRECTORY, destination),
                )
                # bevendo
                scp.get(
                    "{}/bevendo_project/frontend/.env.local".format(settings.DROPLET1_WEB_DIRECTORY),
                    "{}/{}/.env.local".format(settings.BACKUPS_DIRECTORY, destination),
                )
                scp.get(
                    "{}/bevendo_project/backend/bevendo/config/local.py".format(settings.DROPLET1_WEB_DIRECTORY),
                    "{}/{}/bevendo_local.py".format(settings.BACKUPS_DIRECTORY, destination),
                )
                scp.get(
                    "{}/bevendo_project/backend/bevendo/config/prod.py".format(settings.DROPLET1_WEB_DIRECTORY),
                    "{}/{}/bevendo_prod.py".format(settings.BACKUPS_DIRECTORY, destination),
                )
                # bevendo mysql dump
                scp.get(
                    "{}/backups/bevendo-dump.sql.gz".format(settings.DROPLET1_WEB_DIRECTORY),
                    "{}/{}/bevendo-dump.sql.gz".format(settings.BACKUPS_DIRECTORY, destination),
                )
                scp.get(
                    "{}/avvento_project/avvento/avvento/settings/local.py".format(settings.DROPLET1_WEB_DIRECTORY),
                    "{}/{}/avvento_local.py".format(settings.BACKUPS_DIRECTORY, destination),
                )
                scp.get(
                    "{}/avvento_project/avvento/avvento/settings/production.py".format(settings.DROPLET1_WEB_DIRECTORY),
                    "{}/{}/avvento_production.py".format(settings.BACKUPS_DIRECTORY, destination),
                )
                scp.get(
                    "{}/avvento_project/avvento/avvento/db.sqlite3".format(settings.DROPLET1_WEB_DIRECTORY),
                    "{}/{}/avvento_db.sqlite3".format(settings.BACKUPS_DIRECTORY, destination),
                )

                # Apache config files
                scp.get(
                    f'/etc/apache2/ports.conf',
                    f'{settings.BACKUPS_DIRECTORY}/{destination}/ports.conf',
                )
                scp.get(
                    f'/etc/apache2/sites-available/000-default.conf',
                    f'{settings.BACKUPS_DIRECTORY}/{destination}/000-default.conf',
                )
                scp.get(
                    f'/etc/apache2/sites-available/001-default.conf',
                    f'{settings.BACKUPS_DIRECTORY}/{destination}/001-default.conf',
                )
                scp.get(
                    f'/etc/apache2/sites-available/002-default.conf',
                    f'{settings.BACKUPS_DIRECTORY}/{destination}/002-default.conf',
                )
                scp.get(
                    f'/etc/apache2/sites-available/bevendo-backend.conf',
                    f'{settings.BACKUPS_DIRECTORY}/{destination}/bevendo-backend.conf',
                )
                scp.get(
                    f'/etc/apache2/sites-available/bevendo-frontend.conf',
                    f'{settings.BACKUPS_DIRECTORY}/{destination}/bevendo-frontend.conf',
                )
                scp.get(
                    f'/etc/apache2/sites-available/three-strikes-website.conf',
                    f'{settings.BACKUPS_DIRECTORY}/{destination}/three-strikes-website.conf',
                )
                scp.get(
                    f'/etc/apache2/sites-available/whisky-creek-ramblers.conf',
                    f'{settings.BACKUPS_DIRECTORY}/{destination}/whisky-creek-ramblers.conf',
                )
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
    shutil.rmtree("{}/archive-droplet1".format(settings.BACKUPS_DIRECTORY))
    # print("done")

def delete_dropbox_archive():
    # print("removing dropbox archive...")
    shutil.rmtree("{}/archive-droplet1".format(settings.DROPBOX_BACKUPS_DIRECTORY))
    # print("done")

def run():
    errors = []

    try:
        archive_current_backup()
        archive_current_dropbox_backup()
        dir_name = create_new_directory()
        create_new_backup(dir_name)
        copy_backup_to_dropbox(dir_name)
        delete_local_archive()
        delete_dropbox_archive()
    except FileNotFoundError as error:
        errors.append("FileNotFoundError: {}".format(error))
    except TypeError as error:
        errors.append("TypeError: {}".format(error))
    except FileExistsError as error:
        errors.append("FileExistsError: {}".format(error))
    except NameError as error:
        errors.append("NameError: {}".format(error))
    except SCPException as error:
        errors.append("SCPException: {}".format(error))
    except:
        errors.append("Unexpected error: {}".format(sys.exc_info()[0]))

    # success/error logging
    if len(errors) == 0:
        success_message = "{} backed up to local directory {}".format(
            settings.DROPLET1_HOST,
            dir_name,
        )
        # print(success_message)
        logger.info(success_message)
    else:
        error_message = "{} backup encountered the following errors: {}".format(
            settings.DROPLET1_HOST,
            ", ".join(errors),
        )
        # print(error_message)
        logger.error(error_message)

    # print("finis")

run()