#! /usr/bin/env python3

import datetime
import sys
import tomllib
import requests


def iso_8601_timestamp():
    """Format the current time as a second precision ISO 8601 timestamp."""
    return datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat()


def error_and_exit(error):
    print(f"{iso_8601_timestamp()} {error}", file=sys.stderr)
    sys.exit(1)


# Load configuration from the first argument.
try:
    config_path = sys.argv[1]
    with open(config_path, "rb") as fp:
        config = tomllib.load(fp)
    del config_path
except IndexError:
    error_and_exit("Must provide configuration file path as first argument.")
except (FileNotFoundError, OSError, tomllib.TOMLDecodeError) as err:
    error_and_exit(f"Cannot load configuration file: {err}")


def get_ip_address(ip_version) -> str:
    """
    Retrieves the public IP from an API.
    Takes the IP version as an argument (4 or 6)

    Returns a string of the public IP address.
    """
    match ip_version:
        case 4:
            url = "https://api.ipify.org/"
        case 6:
            url = "https://api6.ipify.org/"
        case _:
            raise ValueError(f"Unknown IP version: {ip_version}")

    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        ip_address = r.text
    except TimeoutError as error:
        error_and_exit(error)
    except requests.exceptions.ConnectionError:
        error_and_exit("Connection Error. The internet is probably down.")
    except requests.HTTPError:
        error_and_exit(f"Error getting IP address. HTTP {r.status_code}")
    return ip_address


def check_record(ip_address, ip_version) -> str | None:
    """
    Check DNS records to see if they are up-to-date.
    Takes the expected IP address and the IP version as arguments.

    Returns None if they are up-to-date.
    Returns a string of the hex identifier if they are not.
    """
    match ip_version:
        case 4:
            record_type = "A"
        case 6:
            record_type = "AAAA"
        case _:
            raise ValueError(f"Unknown IP version: {ip_version}")

    url = f"https://api.cloudflare.com/client/v4/zones/{config['zone_identifier']}/dns_records/?type={record_type}&name={config['subdomain']}.{config['domain']}"
    headers = {"Authorization": f"Bearer {config['api_token']}"}

    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        dns_record = r.json()["result"][0]
    except ConnectionError:
        error_and_exit("Connection Error. The internet is probably down.")
    except TimeoutError:
        error_and_exit("Request timed out.")
    except requests.HTTPError:
        error_and_exit(f"Error checking record. HTTP {r.status_code}")

    try:
        if dns_record["content"] == ip_address:
            return None
        else:
            return dns_record["id"]
    except IndexError:
        error_and_exit(
            "Cannot parse response. DNS record probably does not exist, please create it in the Cloudflare Dashboard."
        )


def update_record(identifier, ip_address, ip_version):
    """
    Updates DNS records with new IP address.
    Takes the record identifier, desired IP address and the IP version as arguments.
    """
    match ip_version:
        case 4:
            record_type = "A"
        case 6:
            record_type = "AAAA"
        case _:
            raise ValueError(f"Unknown IP version: {ip_version}")

    url = f"https://api.cloudflare.com/client/v4/zones/{config['zone_identifier']}/dns_records/{identifier}"
    headers = {"Authorization": f"Bearer {config['api_token']}"}
    payload = {
        "type": record_type,
        "name": config["subdomain"],
        "content": ip_address,
        "ttl": 300,
        "proxied": False,
    }

    try:
        r = requests.put(url, headers=headers, json=payload)
        r.raise_for_status()
    except ConnectionError:
        error_and_exit("Connection Error. The internet is probably down.")
    except TimeoutError:
        error_and_exit("Request timed out.")
    except requests.HTTPError:
        error_and_exit(f"Error updating DNS record. HTTP {r.status_code}")

    print(f"{iso_8601_timestamp()} {record_type} record updated to {ip_address}")


# Check and update IPv4 A record.
if config["ipv4_enabled"]:
    ipv4_address = get_ip_address(4)
    record_identity = check_record(ipv4_address, 4)
    if record_identity:
        update_record(record_identity, ipv4_address, 4)

# Check and update IPv6 AAAA record.
if config["ipv6_enabled"]:
    ipv6_address = get_ip_address(6)
    record_identity = check_record(ipv6_address, 6)
    if record_identity:
        update_record(record_identity, ipv6_address, 6)
