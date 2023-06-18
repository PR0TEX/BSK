from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QRadioButton, QDialog
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

from AppWindow.dialogs import CustomDialog
from utils import is_valid_ip, get_own_ip

import Chat.client as client

class AppWindow(QMainWindow):
    def __init__(self):
        self.own_ip = get_own_ip()
        self.partner_ip = ""
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

        send_file_button = QPushButton("Send File - not implemented", self)
        send_file_button.setGeometry(200, 140, 320, 60)
        send_file_button.setStyleSheet(button_style)
        send_file_button.hide()

        logout_button = QPushButton("Logout", self)
        logout_button.setGeometry(200, 240, 320, 60)
        logout_button.setStyleSheet(button_style)
        logout_button.hide()

        # Sending message GUI
        label_message = QLabel(self)
        label_message.setText('Enter message:')
        label_message.setFont(QFont('Tahoma', 15))
        label_message.setAlignment(Qt.AlignCenter)
        label_message.setGeometry(0, 50, 720, 30)
        label_message.hide()

        message_field = QLineEdit(self)
        message_field.setGeometry(140, 110, 440, 50)  # set the position and size of the key_field widget
        message_field.setStyleSheet("background-color: #ffffff; color: #2c2f33; border-radius: 10px; font-family: Arial; font-size: 16px;")
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

            send_message_button.show()
            send_file_button.show()
            logout_button.show()

            pass

        def show_login_gui():
            # hide all visible widgets and unhide all widgets for the login screen
            # remove partner's ip address
            self.partner_ip = ""
            label.show()
            key_field.show()
            create_room_button.show()
            connect_to_room_button.show()

            send_message_button.hide()
            send_file_button.hide()
            logout_button.hide()

        def show_send_message_gui():
            send_message_button.hide()
            send_file_button.hide()
            logout_button.hide()

            label_message.show()
            message_field.show()
            label_encoding.show()
            for opt in radios:
                opt.show()

            confirm_message_button.show()
            back_button.show()

        def show_send_file_gui():
            # TODO: Add file sending functionality
            pass

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
                    self.send_message(self.partner_ip, message_content, encoding)
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
            self.create_room()
            show_user_logged_in_gui()


        # Connect the button press handlers to the buttons
        create_room_button.clicked.connect(create_room_button_pressed)
        connect_to_room_button.clicked.connect(connect_to_room_button_pressed)
        logout_button.clicked.connect(show_login_gui)
        send_message_button.clicked.connect(show_send_message_gui)
        send_file_button.clicked.connect(show_send_file_gui)
        back_button.clicked.connect(show_user_logged_in_gui)
        confirm_message_button.clicked.connect(confirm_message_pressed)


    def create_room(self):
        # Put room creation functionality here
        # Best approach IMO is defining all net related functionality in a separate class

        client.create_room_udp(self.own_ip, 2222)

        print("Created new room!")
        self.partner_ip = ""
        pass

    def connect_to_room(self, ip):
        # Connect to existing room here
        print("Connecting to " + ip + "...")

        # TODO return true if successful
        self.partner_ip = ip
        return True

    def send_message(self, ip, content, encoding):
        # Send message here
        print("we sending messages :D")
        pass

    def message_received(self):
        dlg = CustomDialog()
        dlg.set_title("Yay!")
        dlg.set_message("Message received!")
        dlg.exec()


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle('Fusion')

    window = AppWindow()
    window.show()

    app.exec_()
