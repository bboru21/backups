#!/bin/sh

MAILTO=""

source venv/bin/activate && python backup_sandbox.py --settings=settings_local && deactivate