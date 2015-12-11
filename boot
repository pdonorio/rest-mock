#!/bin/bash

main_command="./run.py"

if [ "$1" == "devel" ]; then
    APP_MODE='development'
fi

if [ "$APP_MODE" == "debug" ]; then
    echo "[=== DEBUG MODE ===]"
    sleep infinity
elif [ "$APP_MODE" == "production" ]; then
    echo "Production !"
## GUNICORN?
    $main_command
else
    echo "Development"
    # API_DEBUG="true" $main_command
    $main_command --debug
fi
