#! /usr/bin/env python3

import requests

# Loads configuration from ./config.py
import config as config

print("Checking DNS for " + config.subdomain + "." + config.zone + "")

ip = requests.get('https://api.ipify.org').text
print('Public IPv4 address is: {}'.format(ip))

