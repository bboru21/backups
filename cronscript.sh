#!/bin/sh

MAILTO=""

source venv/bin/activate
python backup_diskstation.py --settings=settings_local && python backup_sandbox.py --settings=settings_local
deactivate