import socket
import base64
import os
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QRadioButton, QDialog, \
    QFileDialog
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

from threading import Thread

from AppWindow.dialogs import CustomDialog
from utils import is_valid_ip, get_own_ip

from hashlib import md5
from base64 import b64decode
from base64 import b64encode

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA

from time import sleep


class RSAkeys:
    def __init__(self, size):
        key_pair = RSA.generate(size)
        self.public_key = key_pair.public_key().exportKey()
        self.private_key = key_pair.exportKey()

    def get_public_key(self):
        return self.public_key

    def get_private_key(self):
        return self.private_key

    def encrypt_rsa(self, message, public_key):
        key = RSA.importKey(public_key)

        cipher = PKCS1_OAEP.new(key)
        ciphertext = cipher.encrypt(message)

        return ciphertext

    def decrypt_rsa(self, ciphertext, private_key):
        key = RSA.importKey(private_key)
        cipher = PKCS1_OAEP.new(key)

        message = cipher.decrypt(ciphertext)

        return message


class AESCipher:
    def __init__(self, key, mode, iv):
        self.key = md5(key.encode('utf8')).digest()
        self.mode = mode
        self.iv = iv

    def encrypt(self, data):
        if self.mode == "CBC":
            # iv = get_random_bytes(AES.block_size)
            self.cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            cipher_data = b64encode(self.iv + self.cipher.encrypt(pad(data.encode('utf-8'),
            AES.block_size)))
        elif self.mode == "ECB":
            data = pad(data.encode(), AES.block_size)
            cipher = AES.new(self.key, AES.MODE_ECB)
            cipher_data = base64.b64encode(cipher.encrypt(data))
        else:
            return data

        return cipher_data

    def decrypt(self, data):
        if self.mode == "CBC":
            raw = b64decode(data)
            self.cipher = AES.new(self.key, AES.MODE_CBC, raw[:AES.block_size])
            decrypted_data = unpad(self.cipher.decrypt(raw[AES.block_size:]), AES.block_size)
        elif self.mode == "ECB":
            raw = base64.b64decode(data)
            cipher = AES.new(self.key, AES.MODE_ECB)
            decrypted_data = unpad(cipher.decrypt(raw), AES.block_size)
        else:
            return data
        return decrypted_data

class AppWindow(QMainWindow):
    def __init__(self):
        # each app should have a socket bound to it. It will be used in threads to listen for incoming messages.
        self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.own_ip = get_own_ip()
        self.partner_ip = ""
        self.encoding_mode = "None"
        self.rsa_keys = RSAkeys(1024)
        self.sess_key = ""
        self.iv = ''
        self.encryptor = AESCipher(self.sess_key, self.encoding_mode, self.iv)
        self.receive_thread = Thread()
        super().__init__()
        self.setWindowTitle("SCS Project - Encrypted Data Transmission")
        # self.setWindowIcon(QIcon("path/to/favicon.png"))
        self.setFixedSize(720, 540)  # Make the window non-resizable
        self.setStyleSheet("background-color: #2c2f33;")

        label = QLabel(self)
        label.setText('Enter a key:')
        label.setFont(QFont('Tahoma', 15))
        label.setAlignment(Qt.AlignCenter)
        label.setGeometry(0, 100, 720, 30)

        key_field = QLineEdit(self)
        key_field.setGeometry(140, 160, 440, 50)  # set the position and size of the key_field widget
        key_field.setStyleSheet("background-color: #ffffff; color: #2c2f33; border-radius: 10px; font-family: Arial; font-size: 16px;")

        # Stylesheet for all button widgets
        button_style = """
                QPushButton {
                    background-color: #7289da;
                    color: #ffffff;
                    border-radius: 10px;
                    font-family: Arial;
                    font-size: 16px;
                }

                QPushButton:hover {
                    background-color: #4c5f7b;
                }
                """

        # Login page
        create_room_button = QPushButton("Create room", self)
        create_room_button.setGeometry(140, 240, 200, 50)
        create_room_button.setStyleSheet(button_style)

        connect_to_room_button = QPushButton("Connect to room", self)
        connect_to_room_button.setGeometry(380, 240, 200, 50)
        connect_to_room_button.setStyleSheet(button_style)

        # After logging in
        send_message_button = QPushButton("Send Message", self)
        send_message_button.setGeometry(200, 60, 320, 60)
        send_message_button.setStyleSheet(button_style)
        send_message_button.hide()

        send_file_button = QPushButton("Send File", self)
        send_file_button.setGeometry(200, 140, 320, 60)
        send_file_button.setStyleSheet(button_style)
        send_file_button.hide()

        self.logout_button = QPushButton("Logout", self)
        self.logout_button.setGeometry(200, 240, 320, 60)
        self.logout_button.setStyleSheet(button_style)
        self.logout_button.hide()

        # Sending file GUI
        select_file_button = QPushButton("Select file", self)
        select_file_button.setGeometry(200, 60, 320, 60)
        select_file_button.setStyleSheet(button_style)
        select_file_button.hide()

        select_file_prompt = QFileDialog(self)
        select_file_prompt.setStyleSheet("background-color: #ffffff")
        select_file_prompt.hide()

        message_field = QLineEdit(self)
        message_field.setGeometry(140, 110, 440, 50)  # set the position and size of the key_field widget
        message_field.setStyleSheet(
            "background-color: #ffffff; color: #2c2f33; border-radius: 10px; font-family: Arial; font-size: 16px;")
        message_field.hide()

        confirm_file_button = QPushButton("Send file", self)
        confirm_file_button.setGeometry(200, 290, 320, 60)
        confirm_file_button.setStyleSheet(button_style)
        confirm_file_button.hide()

        # Sending message GUI
        label_message = QLabel(self)
        label_message.setText('Enter message:')
        label_message.setFont(QFont('Tahoma', 15))
        label_message.setAlignment(Qt.AlignCenter)
        label_message.setGeometry(0, 50, 720, 30)
        label_message.hide()

        message_field = QLineEdit(self)
        message_field.setGeometry(140, 110, 440, 50)  # set the position and size of the key_field widget
        message_field.setStyleSheet("background-color: #ffffff; color: #2c2f33; border-radius: 10px; font-family: Arial; font-size: 12px;")
        message_field.hide()

        label_encoding = QLabel(self)
        label_encoding.setText('Select encoding:')
        label_encoding.setFont(QFont('Tahoma', 15))
        label_encoding.setAlignment(Qt.AlignCenter)
        label_encoding.setGeometry(0, 180, 720, 30)
        label_encoding.hide()

        ecb_radio = QRadioButton("ECB", self)
        cbc_radio = QRadioButton("CBC", self)
        ecb_radio.setFont(QFont('Tahoma', 15))
        cbc_radio.setFont(QFont('Tahoma', 15))
        ecb_radio.setGeometry(320, 210, 70, 30)
        cbc_radio.setGeometry(320, 240, 70, 30)
        ecb_radio.setChecked(True)

        radios = [ecb_radio, cbc_radio]
        for option in radios:
            option.hide()

        confirm_message_button = QPushButton("Send message", self)
        confirm_message_button.setGeometry(200, 290, 320, 60)
        confirm_message_button.setStyleSheet(button_style)
        confirm_message_button.hide()

        back_button = QPushButton("Back", self)
        back_button.setGeometry(200, 390, 320, 60)
        back_button.setStyleSheet(button_style)
        back_button.hide()

        # TODO:
        #  Create pages for file exchange and for message exchange:
        #  - add field for message content, radio buttons for encoding DONE
        #  - add radio fields for encoding type DONE
        #  - add send buttons DONE
        #  - add file browsing LATER




        # Button press handlers
        def show_user_logged_in_gui():
            # hide all visible widgets and unhide all widgets for the message selection
            label.hide()
            key_field.hide()
            create_room_button.hide()
            connect_to_room_button.hide()

            label_message.hide()
            message_field.hide()
            label_encoding.hide()
            for opt in radios:
                opt.hide()

            confirm_message_button.hide()
            back_button.hide()
            select_file_button.hide()
            confirm_file_button.hide()

            send_message_button.show()
            send_file_button.show()
            self.logout_button.show()

            pass

        def show_login_gui():
            # hide all visible widgets and unhide all widgets for the login screen
            # remove partner's ip address
            #self.partner_ip = ""
            label.show()
            key_field.show()
            create_room_button.show()
            connect_to_room_button.show()
            label_message.hide()
            message_field.hide()
            label_encoding.hide()
            for opt in radios:
                opt.hide()

            confirm_message_button.hide()
            back_button.hide()
            select_file_button.hide()
            confirm_file_button.hide()

            send_message_button.hide()
            send_file_button.hide()
            self.logout_button.hide()

        def logout():
            self.listening_socket.close()
            self.sending_socket.close()

            self.setWindowTitle("SCS Project - Encrypted Data Transmission")

            self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.own_ip = get_own_ip()
            self.partner_ip = ""
            self.encoding_mode = "None"
            self.sess_key = ""
            self.iv = ''
            self.encryptor = AESCipher(self.sess_key, self.encoding_mode, self.iv)
            self.rsa_keys = RSA(1024)

            show_login_gui()

        def show_send_message_gui():
            if self.partner_ip == "":
                dlg = CustomDialog()
                dlg.set_title("No recipient set")
                dlg.set_message("Currently not connected to anybody.")
                dlg.exec()
                return
            send_message_button.hide()
            send_file_button.hide()
            self.logout_button.hide()

            label_message.show()
            message_field.setReadOnly(False)
            message_field.setText("")
            message_field.show()
            label_encoding.show()
            for opt in radios:
                opt.show()

            confirm_message_button.show()
            back_button.show()

        def show_send_file_gui():
            if self.partner_ip == "":
                dlg = CustomDialog()
                dlg.set_title("No recipient set")
                dlg.set_message("Currently not connected to anybody.")
                dlg.exec()
                return
            send_message_button.hide()
            send_file_button.hide()
            self.logout_button.hide()

            select_file_button.show()
            message_field.setReadOnly(True)
            message_field.setText("")
            message_field.show()
            label_encoding.show()
            for opt in radios:
                opt.show()

            confirm_file_button.show()
            back_button.show()

        def show_file_selection_prompt():
            if select_file_prompt.exec():
                fname = select_file_prompt.selectedFiles()[0]
                print(fname)
                message_field.setText(fname)

        def confirm_message_pressed():
            if self.partner_ip == "":
                dlg = CustomDialog()
                dlg.set_title("No recipient set")
                dlg.set_message("Currently not connected to anybody.")
                dlg.exec()
                return

            message_content = message_field.text()
            encoding = "ECB" if ecb_radio.isChecked() else "CBC"

            if message_content == "":
                dlg = CustomDialog()
                dlg.set_message("Cannot send empty message.")
                dlg.exec()
            else:
                dlg = CustomDialog(dialog_type="yes_no")
                dlg.set_message("Encoding: " + encoding + "\tReceiver: " + self.partner_ip)
                dlg.set_title("Send message?")

                if dlg.exec():
                    self.send_message(message_content)
                    show_user_logged_in_gui()
                else:
                    pass

        def confirm_file_pressed():
            if self.partner_ip == "":
                dlg = CustomDialog()
                dlg.set_title("No recipient set")
                dlg.set_message("Currently not connected to anybody.")
                dlg.exec()
                return

            message_content = message_field.text()
            encoding = "ECB" if ecb_radio.isChecked() else "CBC"

            if message_content == "":
                dlg = CustomDialog()
                dlg.set_message("You need to select a file first.")
                dlg.exec()
            else:
                dlg = CustomDialog(dialog_type="yes_no")
                dlg.set_message("Encoding: " + encoding + "\tReceiver: " + self.partner_ip)
                dlg.set_title("Send file?")

                if dlg.exec():
                    self.send_file(file=message_content)
                    show_user_logged_in_gui()
                else:
                    pass

        def connect_to_room_button_pressed():

            ip = key_field.text()

            if is_valid_ip(ip):
                if self.connect_to_room(ip):
                    self.partner_ip = ip
                    show_user_logged_in_gui()
                else:
                    dlg = CustomDialog()
                    dlg.set_message("Error connecting to room!")
                    dlg.exec()

            else:
                dlg = CustomDialog()
                dlg.set_message("The specified ip is invalid.")
                dlg.exec()

        def create_room_button_pressed():
            self.create_room(encoding = "ECB" if ecb_radio.isChecked() else "CBC")
            show_user_logged_in_gui()


        # Connect the button press handlers to the buttons
        create_room_button.clicked.connect(create_room_button_pressed)
        connect_to_room_button.clicked.connect(connect_to_room_button_pressed)
        self.logout_button.clicked.connect(logout)
        send_message_button.clicked.connect(show_send_message_gui)
        send_file_button.clicked.connect(show_send_file_gui)
        back_button.clicked.connect(show_user_logged_in_gui)
        confirm_message_button.clicked.connect(confirm_message_pressed)
        select_file_button.clicked.connect(show_file_selection_prompt)
        confirm_file_button.clicked.connect(confirm_file_pressed)


    def create_popup(self, title, message, mode):
        dlg = CustomDialog(dialog_type=mode) if mode else CustomDialog()
        dlg.set_message(message)
        dlg.set_title(title)
        return dlg


    def connect_to_room(self, ip):
        host = ip # Replace with the server's IP address
        port = 12346  # Replace with the desired port number

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((host, port))
            print('Connected to the server.')
            self.setWindowTitle("Connected to: " + ip)
            self.partner_ip = ip

            # RSA
            client_socket.sendall(self.rsa_keys.public_key)
            print("Sending public key")

            encrypted_sess_key = client_socket.recv(128)
            self.sess_key = self.rsa_keys.decrypt_rsa(encrypted_sess_key, self.rsa_keys.private_key)
            # self.sess_key = client_socket.recv(1024)
            print("Received session key:", self.sess_key)

            encrypted_encoding_mode = client_socket.recv(128)
            self.encoding_mode = self.rsa_keys.decrypt_rsa(encrypted_encoding_mode, self.rsa_keys.private_key).decode('utf-8')
            print("Received encoding mode:", self.encoding_mode)

            encrypted_iv = client_socket.recv(128)
            self.iv = self.rsa_keys.decrypt_rsa(encrypted_iv, self.rsa_keys.private_key)
            print("Received iv:", self.iv)

            self.encryptor = AESCipher(self.sess_key.hex(), self.encoding_mode, self.iv)
            self.sending_socket = client_socket

            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('', 12345))
            server_socket.listen(1)
            client_socket, client_address = server_socket.accept()

            self.listening_socket = client_socket

            receive_thread = Thread(target=receive_messages, args=(self.listening_socket,))
            # receive_thread = Thread(target=receive_file, args=(client_socket, self))
            receive_thread.start()


        except ConnectionRefusedError:
            print('Unable to connect to the server.')
            self.logout_button.click()
            return False

        return True

    def create_room(self, encoding):
        host = ''
        port = 12346
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(1)
        print('Waiting for incoming connections...')

        self.setWindowTitle("Waiting for somebody to connect...")

        client_socket, client_address = server_socket.accept()
        print('Connected to', client_address)
        self.setWindowTitle("Connected to: " + client_address[0])
        self.partner_ip = client_address[0]

        self.listening_socket = client_socket

        self.encoding_mode = encoding

        # RSA
        partner_public_key = self.listening_socket.recv(1024).decode("utf-8")
        # generate session key
        self.sess_key = os.urandom(16)
        # encrypt session key with peer's public key

        encrypted_sess_key = self.rsa_keys.encrypt_rsa(self.sess_key, partner_public_key)
        # send encrypted session key
        self.listening_socket.sendall(encrypted_sess_key)
        print("Sending session key:", self.sess_key)

        encrypted_encoding_mode = self.rsa_keys.encrypt_rsa(self.encoding_mode.encode('utf-8'), partner_public_key)
        self.listening_socket.sendall(encrypted_encoding_mode)
        print("Sending encoding mode:", self.encoding_mode)
        self.iv = get_random_bytes(AES.block_size)

        encrypted_iv = self.rsa_keys.encrypt_rsa(self.iv, partner_public_key)
        self.listening_socket.sendall(encrypted_iv)
        print("Sending encoding mode:", self.encoding_mode)

        self.encryptor = AESCipher(self.sess_key.hex(), self.encoding_mode, self.iv)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((client_address[0], 12345))
        self.sending_socket = client_socket

        self.receive_thread = Thread(target=receive_messages, args=(self.listening_socket,))
        #receive_thread = Thread(target=receive_file, args=(client_socket,))
        self.receive_thread.start()

    def send_message(self, content):
        # Send message here
        try:
            self.sending_socket.sendall(self.encryptor.encrypt(content))
        except:
            print('An error occurred while sending message.')
            self.logout_button.click()
            self.listening_socket.close()

    def send_file(self, file):

        print("sending file...")
        file_name = file.split("/")[-1]
        # file = open(file_name, "rb")
        file_size = os.path.getsize(file)

        self.sending_socket.send(file_name.encode("utf-8"))
        self.sending_socket.send(str(file_size).encode("utf-8"))

        sleep(1)

        print("will send", math.ceil(file_size / 1024), "packets")
        i = 0
        with open(file, "rb") as f:
            while True:
                data = f.read(1024)
                if not data:
                    self.sending_socket.send(b"<END>")
                    break

                self.sending_socket.send(data)
                i += 1

                window.progressBar.setValue(math.ceil(i / (file_size / 1024) * 100))
                # progress bar update here

        print("sent", i, "packets")


def receive_file(listening_socket):
    global window
    file_name = listening_socket.recv(1024).decode("utf-8")
    print(file_name)
    file_size = listening_socket.recv(1024).decode("utf-8")
    print(file_size)

    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    with open(os.path.join("downloads", f"recv_{file_name}"), "w") as f:
        i = 0
        while True:
            data = listening_socket.recv(1024).decode("utf-8")
            if data.encode("utf-8")[-5:] == b"<END>":
                f.write(data[:-5])
                break
            f.write(data)
            i += 1
            window.progressBar.setValue(math.ceil(i / (file_size / 1024) * 100))
            # sleep(1)

    print("done")


def receive_messages(listeninig_socket):
    global window
    while True:
        try:
            # CBC
            ciphertext = listeninig_socket.recv(1024)
            # Generate the same key used by the server

            # message = decrypt_cbc(key, ciphertext).decode('utf-8')
            # ECB
            message = window.encryptor.decrypt(ciphertext)

            window.create_popup("Message received!", message.decode("utf-8"), "ok").exec()

            print(message)
        except:
            print('An error occurred while receiving messages.')
            window.logout_button.click()
            break




if __name__ == "__main__":
    global window
    app = QApplication([])
    app.setStyle('Fusion')

    window = AppWindow()
    window.show()

    app.exec()
