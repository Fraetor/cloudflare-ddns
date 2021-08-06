#! /usr/bin/env bash
# Requires bash 4 or greater!

python3 ddns.py |& tee -a $1
