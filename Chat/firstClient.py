import socket
import os

room_socket = None
BUFFER_SIZE = 4096

def create_room_udp(ip, port):
    global room_socket
    room_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    room_socket.bind((ip, port))

def create_room_tcp(ip, port):
    global room_socket
    room_socket = socket.socket()
    room_socket.bind((ip, port))


def send_message(ip, port, socket, message):
    response = socket.sendto(message.encode(), (ip, port))
    if response:
        print("message successfully send\n")

def send_file(filename, ip, port):
    global room_socket
    # with open(filename, "rb") as file:
    #     # Read and send the file in chunks
    #     chunk = file.read(1024)
    #     while chunk:
    #         room_socket.send(chunk)
    #         chunk = file.read(1024)
    filesize = os.path.getsize(filename)
    create_room_tcp("192.168.1.24", 2222)
    room_socket.sendto(f"{filename}".encode(), ip, port)

def receive_file():
    create_room_tcp("192.168.1.24", 2222)
    response = room_socket.recvfrom(BUFFER_SIZE)
    while True:
        if response:
            client_socket, address = room_socket.accept()
            filename = client_socket.recv(BUFFER_SIZE).decode()
            filename = os.path.basename(filename)
            break

    with open(filename, "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = client_socket.recv(BUFFER_SIZE)
            if not bytes_read:
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)


def start_room():
    print("Room started")
    while True:
        response = room_socket.recvfrom(1024)
        if response:
            data, address = response
            data = data.decode("ascii")
            print("Received message:", data, "\n")

            dest_ip = address[0]
            dest_port = address[1]
            do_replay = int(input("If you wanna replay insert 1 else 2\n"))
            if do_replay == 1:
                message = input("Insert message\n")
                send_message(dest_ip, dest_port, room_socket, message)
            else:
                break

# DODAC OBSLUGE KIEDY POKOJ ZOSTANIE ZAMKNIETY
def close_room():
    print("Room closed")
    room_socket.close()


def main():
    create_room_tcp("192.168.1.24", 2222)
    receive_file()
    # start_room()
    close_room()


if __name__ == "__main__":
    main()