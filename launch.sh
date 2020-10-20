#!/usr/bin/env bash

wrk_dir="${PWD}"

# Entering virtualenv
echo "Setting up virtualenv..."
test -f "${wrk_dir}/venv/bin/activate" || \
    python3 -m ${wrk_dir}/venv venv
source ${wrk_dir}/venv/bin/activate

# Checking dependencies and install them in virtualenv
echo "Checking dependencies..."
pip3 install -r ${wrk_dir}/requirements.txt &>/dev/null

# Setting up database
echo "Setting up database..."
test -f "${wrk_dir}/konta.db" || \
    python3 ${wrk_dir}/setup.py

# Creating secret key
echo "Setting up secret key..."
test -f "${wrk_dir}/secret_key" || \
    python -c "import os; print(os.urandom(16).hex())" > "${wrk_dir}/secret_key"

echo "Done."
echo ""
# Launching app
cd "${wrk_dir}"
gunicorn --bind "0.0.0.0:5000" "app:app"
