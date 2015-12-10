#!/bin/bash

if [ "$APP_MODE" == "development" ]; then
    echo "Development"
else
    echo "Production !"
fi
