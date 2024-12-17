# Cloudflare dDNS

A python script to update cloudflare DNS to provide dynamic DNS.

# Usage

Make a copy of `example_config.toml` and fill in your details. Then just run `python3 ddns.py /path/to/config.toml`.

For final deployments I would recommend setting up a `cron` job to run the script every so often.

# Requirements

* Python >= 3.11
* [Requests](https://requests.readthedocs.io/)
