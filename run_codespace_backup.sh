#!/bin/sh

MAILTO=""

source venv/bin/activate && python backup_codespace.py --settings=settings_local && deactivate