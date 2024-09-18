#!/bin/bash

python_version=$(python3 --version 2>&1 | awk '{print $2}')
if [[ "$python_version" < "3.12.0" ]]; then
    echo "Installing Python 3.12.0..."
    curl -O https://www.python.org/ftp/python/3.12.0/python-3.12.0-macos11.pkg
    sudo installer -pkg python-3.12.0-macos11.pkg -target /
    echo "Python 3.12.0 has been successfully installed."
    rm python-3.12.0-macos11.pkg
else
    echo "Python version is already up to date."
fi
