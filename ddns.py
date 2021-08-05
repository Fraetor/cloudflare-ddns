#! /usr/bin/env python3

import requests
from requests.structures import CaseInsensitiveDict
from time import strftime

# Loads configuration from ./config.py
import config as config


def get_ipv4_address():
    return requests.get("https://api.ipify.org").text


def get_ipv6_address():
    return requests.get("https://api6.ipify.org").text


def check_record(ip_address, ip_version=4):
    """
    Check DNS records to see if they are up-to-date.
    Takes the expected IP address and the IP version as arguments.

    Returns None if they are up-to-date.
    Returns a string of the hex identifier if they are not.
    """
    if ip_version == 4:
        record_type = "A"
    elif ip_version == 6:
        record_type = "AAAA"
    else:
        raise ValueError
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Bearer " + config.api_token
    url = "https://api.cloudflare.com/client/v4/zones/" + config.zone_identifier + \
        "/dns_records/?type=" + record_type + "&name=" + \
        config.subdomain + "." + config.domain
    dns_json = requests.get(url, headers=headers).json()["result"][0]
    identifier = dns_json["id"]
    dns_address = dns_json["content"]
    if dns_address == ip_address:
        return None
    else:
        return identifier


def update_record(identifier, ip_address, ip_version=4):
    """
    Updates DNS records with new IP address.
    Takes the record identifier, desired IP address and the IP version as arguments.

    Returns the HTTP status code if an error occurs.
    Returns None otherwise.
    """
    if ip_version == 4:
        record_type = "A"
    elif ip_version == 6:
        record_type = "AAAA"
    else:
        raise ValueError
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Bearer " + config.api_token
    payload = {"type": record_type, "name": config.subdomain,
               "content": ip_address, "ttl": 300, "proxied": False}
    url = "https://api.cloudflare.com/client/v4/zones/" + \
        config.zone_identifier + "/dns_records/" + identifier
    r = requests.put(url, headers=headers, json=payload)
    if r.status_code != 200:
        print("Error updating DNS record. HTTP " + str(r.status_code))
        return r.status_code
    return None


# Check and update IPv4 A record.
if config.ipv4_enabled:
    ipv4_address = get_ipv4_address()
    ident = check_record(ipv4_address, 4)
    if ident != None:
        if update_record(ident, ipv4_address, 4) == None:
            current_time = strftime("%Y-%m-%d %H:%M:%S %Z")
            print(current_time + " A record updated to " + ipv4_address)


# Check and update IPv6 AAAA record.
if config.ipv6_enabled:
    ipv6_address = get_ipv6_address()
    ident = check_record(ipv6_address, 6)
    if ident != None:
        if update_record(ident, ipv6_address, 6) == None:
            current_time = strftime("%Y-%m-%d %H:%M:%S %Z")
            print(current_time + " AAAA record updated to " + ipv6_address)
