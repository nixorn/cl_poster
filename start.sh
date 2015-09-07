#!/bin/sh

cd /root/craglist-poster
scl enable python27 'which python'
scl enable python27 'python --version'
scl enable python27 bash
source /opt/rh/python27/enable
. venv/bin/activate
python tornado_deploy.py
