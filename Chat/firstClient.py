import socket
import os
import threading

room_socket = None
BUFFER_SIZE = 4096

import socket
import threading

# Server configuration
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8001

# Create a socket for the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(1)

# List to store connected clients
clients = []

def broadcast(message):
    """Send a message to all connected clients."""
    for client in clients:
        client.send(message)

def handle_client(client_socket, client_address):
    """Handles a client connection."""
    while True:
        try:
            message = client_socket.recv(1024)
            broadcast(message)
        except:
            # Client has disconnected
            index = clients.index(client_socket)
            clients.remove(client_socket)
            client_socket.close()
            broadcast(f'Client {client_address} has left the chat.'.encode('utf-8'))
            break

def accept_connections():
    """Accept incoming connections from clients."""
    while True:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        print(f'Client {client_address} has connected to the server.')
        client_socket.send('Welcome to the chat!'.encode('utf-8'))
        broadcast(f'Client {client_address} has joined the chat.'.encode('utf-8'))
        client_socket.send('Start chatting!'.encode('utf-8'))
        threading.Thread(target=handle_client, args=(client_socket, client_address)).start()

def start_server():
    """Start the server to listen for incoming connections."""
    print('Server is running...')
    accept_connections()


#
#
# def create_room_tcp(ip, port):
#     global room_socket
#     room_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     room_socket.bind((ip, port))
#
# def handle_client(peer_socket, peer_address):
#     print(f"Connected with {peer_address[0]}:{peer_address[1]}")
#
#     while True:
#         response = peer_socket.recv(1024).decode("utf-8")
#         if not response:
#             break
#         print(f"Received message from {peer_address[0]}:{peer_address[1]} ", response, "\n")
#
#         do_replay = int(input("If you wanna replay insert 1 else 2\n"))
#         if do_replay == 1:
#             message = input("Insert message\n")
#             send_message(peer_address[0], peer_address[1], peer_socket, message)
#         else:
#             break
#
#     peer_socket.close()
#     print(f"Connection closed with {peer_address[0]}:{peer_address[1]}")
#
# def create_room_udp(host, port):
#     global room_socket
#     # TCP
#     room_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     room_socket.bind((host, port))
#     room_socket.listen()
#
#     while True:
#         client_socket, client_address = room_socket.accept()
#         client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
#         client_thread.start()
#
#
#
# def send_message(ip, port, socket, message):
#     response = socket.sendto(message.encode("utf-8"), (ip, port))
#     if response:
#         print("message successfully send\n")
#
# def send_message(socket, message):
#     response = socket.send(message.encode("utf-8"))
#     if response:
#         print("message successfully send\n")
#
# def send_file(filename, ip, port):
#     global room_socket
#     # with open(filename, "rb") as file:
#     #     # Read and send the file in chunks
#     #     chunk = file.read(1024)
#     #     while chunk:
#     #         room_socket.send(chunk)
#     #         chunk = file.read(1024)
#     filesize = os.path.getsize(filename)
#     create_room_tcp("192.168.1.24", 2222)
#     room_socket.sendto(f"{filename}".encode(), ip, port)
#
#
# def start_room():
#     print("Room started")
#     while True:
#         response = room_socket.recvfrom(1024)
#         if response:
#             data, address = response
#             data = data.decode("ascii")
#             print("Received message:", data, "\n")
#
#             dest_ip = address[0]
#             dest_port = address[1]
#             do_replay = int(input("If you wanna replay insert 1 else 2\n"))
#             if do_replay == 1:
#                 message = input("Insert message\n")
#                 send_message(dest_ip, dest_port, room_socket, message)
#             else:
#                 break
#
# # DODAC OBSLUGE KIEDY POKOJ ZOSTANIE ZAMKNIETY
# def close_room():
#     print("Room closed")
#     room_socket.close()
#
#
# def main():
#     ip = input("Insert ip")
#     create_room_udp(ip, 2222)
#     # receive_file()
#     # start_room()
#     # close_room()
#
#     my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     # room_ip = input("Enter IP to start chat\n")
#     # room_port = 2222
#     my_socket.connect((ip, 2222))
#     init_message = input("Enter message")
#     print("Client started\n")
#     send_message(my_socket, init_message)



if __name__ == "__main__":
    start_server()