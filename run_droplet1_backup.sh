#!/bin/sh

MAILTO=""

source venv/bin/activate && python backup_droplet1.py --settings=settings_local && deactivate