#!/usr/bin/sh

test -f "konta.db"
if [ $? == 1 ]; then
    python3 setup.py
fi

python3 app.py
