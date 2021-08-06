# Cloudflare dDNS
A python script to update cloudflare DNS to provide dynamic DNS.

# Usage
Make a copy of `example_config.py` named `config.py` and fill in your details.
Then just run `python3 ddns.py`
For final deployments I would recommend setting up a `cron` job to run the script every so often.

A bash script is included for running with `cron`, which also includes logging of errors to the specified file.
```sh
$ ./sync.sh /path/to/log/file
```

# Requirements
Python >3.6 (Tested with 3.9)

[Requests](https://requests.readthedocs.io/)
```
pip3 install requests
```