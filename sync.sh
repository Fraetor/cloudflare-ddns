#! /usr/bin/env bash
# Requires bash 4 or greater!

# Change working directory to script's location.
cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null 

# Run DDNS updater.
python3 ddns.py |& tee -a $1
