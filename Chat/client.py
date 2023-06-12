import socket

s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    ip, port = input("Enter server ip and port number").split()
    message = input("Enter message: ")
    response = s.sendto(message.encode(), ("{IP_ADDRESS}",2222))
    if response:
        print("\nsuccessfully send to server")