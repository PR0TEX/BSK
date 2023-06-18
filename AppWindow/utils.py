import re
def is_valid_ip(ip):
    match = re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip)
    return bool(match)
