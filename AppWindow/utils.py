import re
import socket


def is_valid_ip(ip):
    match = re.match(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", ip)
    return bool(match)

def get_own_ip():
    return socket.gethostbyname(socket.gethostname())