#!/bin/bash

main_command="./run.py"

if [ "$APP_MODE" == "debug" ]; then
    echo "[=== DEBUG MODE ===]"
    sleep infinity
elif [ "$APP_MODE" == "development" ]; then
    echo "Development"
    # API_DEBUG="true" $main_command
    $main_command --debug
else
    echo "Production !"
## GUNICORN?
    $main_command
fi
