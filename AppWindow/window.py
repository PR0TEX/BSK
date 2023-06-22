import socket
import base64
import os
import math
import struct

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QRadioButton, QDialog, \
    QFileDialog, QProgressBar
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

    def encrypt(self, data, encoding="utf-8"):
        if self.mode == "CBC":
            self.cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            cipher_data = b64encode(self.iv + self.cipher.encrypt(pad(data.encode(encoding), AES.block_size)))
        elif self.mode == "ECB":
            data = pad(data.encode(encoding), AES.block_size)
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
        self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.own_ip = get_own_ip()
        self.partner_ip = ""
        self.encoding_mode = "None"
        self.rsa_keys = RSAkeys(1024)
        self.sess_key = ""
        self.iv = ""
        self.encryptor = AESCipher(self.sess_key, self.encoding_mode, self.iv)
        self.receive_thread = Thread()
        super().__init__()
        self.setWindowTitle("SCS Project - Encrypted Data Transmission (Not connected)")
        # self.setWindowIcon(QIcon("path/to/favicon.png"))
        self.setFixedSize(720, 540)  # Make the window non-resizable
        self.setStyleSheet("background-color: #2c2f33; color: #f0f0f0;")

        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(0, 500, 720, 40)

        label = QLabel(self)
        label.setText('Enter IP:')
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

        label_encoding = QLabel(self)
        label_encoding.setText('Select encoding:')
        label_encoding.setFont(QFont('Tahoma', 15))
        label_encoding.setAlignment(Qt.AlignCenter)
        label_encoding.setGeometry(0, 300, 720, 30)

        ecb_radio = QRadioButton("ECB", self)
        cbc_radio = QRadioButton("CBC", self)
        ecb_radio.setFont(QFont('Tahoma', 15))
        cbc_radio.setFont(QFont('Tahoma', 15))
        ecb_radio.setGeometry(320, 340, 70, 30)
        cbc_radio.setGeometry(320, 370, 70, 30)
        ecb_radio.setChecked(True)

        radios = [ecb_radio, cbc_radio]

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
        message_field.setGeometry(140, 130, 440, 50)  # set the position and size of the key_field widget
        message_field.setStyleSheet("background-color: #ffffff; color: #2c2f33; border-radius: 10px; font-family: Arial; font-size: 12px;")
        message_field.hide()


        confirm_message_button = QPushButton("Send message", self)
        confirm_message_button.setGeometry(200, 290, 320, 60)
        confirm_message_button.setStyleSheet(button_style)
        confirm_message_button.hide()

        back_button = QPushButton("Back", self)
        back_button.setGeometry(200, 390, 320, 60)
        back_button.setStyleSheet(button_style)
        back_button.hide()

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
            self.partner_ip = ""
            label.show()
            key_field.show()
            create_room_button.show()
            connect_to_room_button.show()
            label_message.hide()
            message_field.hide()
            label_encoding.show()
            for opt in radios:
                opt.show()

            confirm_message_button.hide()
            back_button.hide()
            select_file_button.hide()
            confirm_file_button.hide()

            send_message_button.hide()
            send_file_button.hide()
            self.logout_button.hide()

        def logout():
            try:
                self.sending_socket.send(self.encryptor.encrypt(b"<ENDCHAT>".decode("utf-8")))
            except Exception as error:
                # print(error)
                pass

            self.listening_socket.close()
            self.sending_socket.close()

            self.setWindowTitle("SCS Project - Encrypted Data Transmission (Not connected)")

            self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.own_ip = get_own_ip()
            self.partner_ip = ""
            self.encoding_mode = "None"
            self.sess_key = ""
            self.iv = ""
            self.rsa_keys = RSAkeys(1024)
            self.encryptor = AESCipher(self.sess_key, self.encoding_mode, self.iv)

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

            confirm_message_button.show()
            back_button.show()
            self.setWindowTitle("Connected to: " + self.partner_ip)

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

            confirm_file_button.show()
            back_button.show()
            self.setWindowTitle("Connected to: " + self.partner_ip)

        def show_file_selection_prompt():
            if select_file_prompt.exec():
                fname = select_file_prompt.selectedFiles()[0]
                # print(fname)
                message_field.setText(fname)

        def confirm_message_pressed():
            if self.partner_ip == "":
                dlg = CustomDialog()
                dlg.set_title("No recipient set")
                dlg.set_message("Currently not connected to anybody.")
                dlg.exec()
                return

            message_content = message_field.text()

            if message_content == "":
                dlg = CustomDialog()
                dlg.set_message("Cannot send empty message.")
                dlg.exec()
            else:
                dlg = CustomDialog(dialog_type="yes_no")
                dlg.set_message("Encoding: " + self.encoding_mode + "\tReceiver: " + self.partner_ip)
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

            if message_content == "":
                dlg = CustomDialog()
                dlg.set_message("You need to select a file first.")
                dlg.exec()
            else:
                dlg = CustomDialog(dialog_type="yes_no")
                dlg.set_message("Encoding: " + self.encoding_mode + "\tReceiver: " + self.partner_ip)
                dlg.set_title("Send file?")

                if dlg.exec():
                    self.send_file(file=message_content)
                    show_user_logged_in_gui()
                else:
                    pass

        def connect_to_room_button_pressed():
            self.encoding_mode = "ECB" if ecb_radio.isChecked() else "CBC"
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
            self.encoding_mode = "ECB" if ecb_radio.isChecked() else "CBC"
            self.create_room()
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
            print('Connected to ' + ip)
            self.setWindowTitle("Connected to: " + ip)
            self.partner_ip = ip

            # RSA
            client_socket.send(self.rsa_keys.public_key)
            print("Sending public key")

            encrypted_sess_key = client_socket.recv(128)
            self.sess_key = self.rsa_keys.decrypt_rsa(encrypted_sess_key, self.rsa_keys.private_key)
            print("Received session key:", self.sess_key)

            encrypted_encoding_mode = client_socket.recv(128)
            self.encoding_mode = self.rsa_keys.decrypt_rsa(encrypted_encoding_mode, self.rsa_keys.private_key).decode(
                'utf-8')
            print("Received encoding mode:", self.encoding_mode)

            encrypted_iv = client_socket.recv(128)
            self.iv = self.rsa_keys.decrypt_rsa(encrypted_iv, self.rsa_keys.private_key)
            if self.encoding_mode == "CBC":
                print("Received iv:", self.iv)

            self.encryptor = AESCipher(self.sess_key.hex(), self.encoding_mode, self.iv)
            self.sending_socket = client_socket

            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('', 12345))
            server_socket.listen(1)
            client_socket, client_address = server_socket.accept()

            self.listening_socket = client_socket

            receive_thread = Thread(target=receive_messages, args=(self.listening_socket,))
            receive_thread.start()


        except ConnectionRefusedError:
            print('Unable to connect to the server.')
            self.logout_button.click()
            return False

        return True

    def create_room(self):
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

        partner_public_key = self.listening_socket.recv(1024).decode("utf-8")
        self.sess_key = os.urandom(16)

        encrypted_sess_key = self.rsa_keys.encrypt_rsa(self.sess_key, partner_public_key)
        self.listening_socket.send(encrypted_sess_key)
        print("Sending session key:", self.sess_key)

        encrypted_encoding_mode = self.rsa_keys.encrypt_rsa(self.encoding_mode.encode('utf-8'), partner_public_key)
        self.listening_socket.send(encrypted_encoding_mode)
        print("Sending encoding mode:", self.encoding_mode)
        self.iv = get_random_bytes(AES.block_size)

        encrypted_iv = self.rsa_keys.encrypt_rsa(self.iv, partner_public_key)
        self.listening_socket.send(encrypted_iv)

        if self.encoding_mode == "CBC":
            print("Sending iv vector:", self.iv)

        self.encryptor = AESCipher(self.sess_key.hex(), self.encoding_mode, self.iv)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((client_address[0], 12345))
        self.sending_socket = client_socket

        self.receive_thread = Thread(target=receive_messages, args=(self.listening_socket,))
        self.receive_thread.start()

    def send_message(self, content):
        try:
            self.sending_socket.send(self.encryptor.encrypt(content))
            self.setWindowTitle(self.windowTitle()+" -- Message sent!")
        except:
            print('An error occurred while sending the message.')
            self.logout_button.click()

    def send_file(self, file):
        i = 0
        try:
            print("sending file...")
            file_name = file.split("/")[-1]
            file_size = os.path.getsize(file)

            self.sending_socket.send(self.encryptor.encrypt(b"<FILE>".decode("utf-8")))
            sleep(0.1)
            self.sending_socket.send(self.encryptor.encrypt(file_name))
            sleep(0.1)
            self.sending_socket.send(self.encryptor.encrypt(str(file_size)))
            sleep(0.1)
            self.setWindowTitle(self.windowTitle() + " -- sending file "+file_name+"...")
            print("will send", math.ceil(file_size / (1024 * 4)), "packets")
            with open(file, "rb") as f:
                while True:
                    data = f.read(1024 * 4)
                    if not data:
                        encrypted_data = self.encryptor.encrypt(b"<END>".decode("utf-8"))
                        encrypted_data = struct.pack('>I', len(encrypted_data)) + encrypted_data
                        self.sending_socket.send(encrypted_data)

                        window.progressBar.setValue(100)
                        break

                    try:
                        encrypted_data = self.encryptor.encrypt(data.decode("utf-8"))
                    except:
                        encrypted_data = self.encryptor.encrypt(data.decode("latin-1"), "latin-1")

                    encrypted_data = struct.pack('>I', len(encrypted_data)) + encrypted_data
                    self.sending_socket.send(encrypted_data)
                    #sleep(1/100)
                    i += 1
                    window.progressBar.setValue(math.ceil(i / (file_size / (1024 * 4)) * 100))

            print("sent", i, "packets")

        except Exception as error:
            print("There was an error while sending the file")
            self.logout_button.click()
        finally:
            self.setWindowTitle("Connected to: "+self.partner_ip+" -- file sent!")


def recv_msg(sock):
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]

    return recvall(sock, msglen)


def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def receive_messages(listening_socket):
    global window
    while True:
        i = 0
        try:
            ciphertext = listening_socket.recv(1024)
            message = window.encryptor.decrypt(ciphertext)

            if message == b"<FILE>":
                file_name = listening_socket.recv(1024)
                file_name = window.encryptor.decrypt(file_name).decode("utf-8")

                file_size = listening_socket.recv(1024)
                file_size = window.encryptor.decrypt(file_size).decode("utf-8")

                window.setWindowTitle(window.windowTitle() + " -- downloading file " + file_name + "...")

                if not os.path.exists("downloads"):
                    os.makedirs("downloads")

                received_amount = 0
                with open(os.path.join("downloads", f"recv_{file_name}"), "wb") as f:
                    while True:
                        data = recv_msg(listening_socket)
                        data = window.encryptor.decrypt(data)
                        received_amount += len(data)
                        if data[-5:] == b"<END>":
                            f.write(data[:-5])
                            window.progressBar.setValue(100)
                            break
                        f.write(data)
                        i += 1
                        window.progressBar.setValue(math.ceil(received_amount / (int(file_size)) * 100))


                window.setWindowTitle("Connected to: " + window.partner_ip + " -- file received!")
            elif message == b"<ENDCHAT>":
                window.logout_button.click()
                return
            else:
                window.setWindowTitle("Connected to: " + window.partner_ip + " -- Message: " + message.decode("utf-8"))
        except Exception as error:
            window.logout_button.click()
            break



if __name__ == "__main__":
    global window
    app = QApplication([])
    app.setStyle('Fusion')

    window = AppWindow()
    window.show()

    app.exec()
