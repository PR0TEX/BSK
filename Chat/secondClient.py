import socket
import os

my_socket = None
BUFFER_SIZE = 4096

def send_message(ip, port, socket, message):
    response = socket.sendto(message.encode(), (ip, port))
    if response:
        print("message successfully send\n")

def send_file(ip, port, filename):
    # with open(filename, "rb") as file:
    #     # Read and send the file in chunks
    #     chunk = file.read(1024)
    #     while chunk:
    #         room_socket.send(chunk)
    #         chunk = file.read(1024)
    filesize = os.path.getsize(filename)
    my_socket = socket.socket()
    my_socket.connect((ip, port))
    my_socket.sendto(f"{filename}".encode(), (ip, port))
    with open(filename, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in
            # busy networks
            my_socket.sendall(bytes_read)


def reply_message():
    while True:
        response = my_socket.recvfrom(1024)
        if response:
            data, address = response
            data = data.decode("ascii")
            print("Received message:", data, "\n")

            dest_ip = address[0]
            dest_port = address[1]
            do_replay = int(input("If you wanna replay insert 1 else 2\n"))

            if do_replay == 1:
                message = input("Insert message\n")
                send_message(dest_ip, dest_port, my_socket, message)
            else:
                break

def replay_file(filename):
    with open(filename, "rb") as file:
        # Read and send the file in chunks
        chunk = file.read(1024)
        while chunk:
            my_socket.send(chunk)
            chunk = file.read(1024)


def close_room():
    print("Disconnected")
    my_socket.close()

def main():
    global my_socket
    # my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    room_ip = input("Enter IP to start chat\n")
    room_port = 2222
    # init_message = input("Enter message \n")
    # print("Connection started\n")
    # send_message(room_ip, room_port, my_socket, init_message)
    # reply_message()

    send_file(room_ip, room_port, "test.txt")


if __name__ == "__main__":
    main()