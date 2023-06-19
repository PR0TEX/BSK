import socket
import os

my_socket = None
BUFFER_SIZE = 4096

def send_message(message):
    response = my_socket.send(message.encode("utf-8"))
    if response:
        print("message successfully send\n")

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
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    room_ip = input("Enter IP to start chat\n")
    room_port = 2222
    my_socket.connect((room_ip,room_port))
    init_message = input("Enter message")
    print("Connection started\n")
    send_message(init_message)
    # reply_message()

    # send_file(room_ip, room_port, "./test.txt")


if __name__ == "__main__":
    main()