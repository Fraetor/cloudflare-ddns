#! /usr/bin/env python3

import requests
from requests.structures import CaseInsensitiveDict
from time import strftime
from sys import stderr

# Loads configuration from ./config.py
import config


def error_and_exit(error):
    print(f"{strftime('%Y-%m-%d %H:%M:%S %Z')} {error}", file=stderr)
    exit(1)


def get_ip_address(ip_version=4):
    """
    Retrieves the public IP from an API.
    Takes the IP version as an argument (4 or 6)

    Returns a string of the public IP address.
    """
    if ip_version == 4:
        url = "https://api.ipify.org/"
    elif ip_version == 6:
        url = "https://api6.ipify.org/"
    else:
        raise ValueError("Invalid IP version.")
    try:
        ip = requests.get(url, timeout=30).text
    except TimeoutError as error:
        error_and_exit(error)
    except requests.exceptions.ConnectionError as error:
        error_and_exit("Connection Error. The internet is probably down.")
    return ip


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
    headers["Authorization"] = f"Bearer {config.api_token}"
    url = f"https://api.cloudflare.com/client/v4/zones/{config.zone_identifier}" + \
        f"/dns_records/?type={record_type}&name={config.subdomain}.{config.domain}"
    try:
        dns_json = requests.get(url, headers=headers, timeout=30).json()[
            "result"][0]
    except ConnectionError as error:
        #error_and_exit(error)
        error_and_exit("Connection Error. The internet is probably down.")
    except TimeoutError as error:
        error_and_exit(error)
    except IndexError as error:
        print("DNS record probably does not exist. Please create it in the Cloudflare Dashboard.")
        error_and_exit(error)
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
    headers["Authorization"] = f"Bearer {config.api_token}"
    payload = {
        "type": record_type,
        "name": config.subdomain,
        "content": ip_address,
        "ttl": 300,
        "proxied": False
    }
    url = f"https://api.cloudflare.com/client/v4/zones/{config.zone_identifier}/dns_records/{identifier}"
    r = requests.put(url, headers=headers, json=payload)
    if r.status_code != 200:
        print(f'{strftime("%Y-%m-%d %H:%M:%S %Z")} Error updating DNS record. HTTP {r.status_code}', file=stderr)
        return r.status_code
    return None


# Check and update IPv4 A record.
if config.ipv4_enabled:
    ipv4_address = get_ip_address(4)
    ident = check_record(ipv4_address, 4)
    if ident:
        if update_record(ident, ipv4_address, 4) is None:
            print(
                f"{strftime('%Y-%m-%d %H:%M:%S %Z')} A record updated to {ipv4_address}")


# Check and update IPv6 AAAA record.
if config.ipv6_enabled:
    ipv6_address = get_ip_address(6)
    ident = check_record(ipv6_address, 6)
    if ident:
        if update_record(ident, ipv6_address, 6) is None:
            print(
                f"{strftime('%Y-%m-%d %H:%M:%S %Z')} AAAA record updated to {ipv6_address}")

exit(0)
