#!/bin/sh

MAILTO=""

source venv/bin/activate && python backup_local.py --settings=settings_local && deactivate