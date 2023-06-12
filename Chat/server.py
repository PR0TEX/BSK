import socket
# AF_INET used for ipv4
# SOCK_DGRAM used for UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

s.bind(("IP_ADDRESS",2222))
print("Server started")
while True:
    print(s.recvfrom(1024))
