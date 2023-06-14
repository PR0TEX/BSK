import socket

room_socket = None

def create_room(ip, port):
    global room_socket
    room_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    room_socket.bind((ip, port))


def send_message(ip, port, socket, message):
    response = socket.sendto(message.encode(), (ip, port))
    if response:
        print("message successfully send\n")

def send_file(filename):
    with open(filename, "rb") as file:
        # Read and send the file in chunks
        chunk = file.read(1024)
        while chunk:
            room_socket.send(chunk)
            chunk = file.read(1024)

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
    create_room("192.168.1.24", 2222)
    start_room()
    close_room()


if __name__ == "__main__":
    main()