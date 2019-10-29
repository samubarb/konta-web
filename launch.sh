#!/usr/bin/env bash

# Entering virtualenv
test -f "venv/bin/activate"
if [ $? == 1 ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Checking dependencies
pip3 install -r requirements.txt --upgrade

# Setting up database
test -f "konta.db"
if [ $? == 1 ]; then
    python3 setup.py
fi

# Creating secret key
python -c 'import os; print(os.urandom(16).hex())' > secret_key

# Launching app
gunicorn -b 0.0.0.0:5000 app:app
