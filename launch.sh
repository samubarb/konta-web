#!/usr/bin/sh

# Entering virtualenv
test -f "venv/bin/activate"
if [ $? == 1 ]; then
    python3 -m venv venv
fi
. ./venv/bin/activate

# Checking dependencies
pip3 install -r requirements.txt --upgrade

# Setting up database
test -f "konta.db"
if [ $? == 1 ]; then
    python3 setup.py
fi

# Launching app
python3 app.py
