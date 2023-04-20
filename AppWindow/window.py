from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QRadioButton
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt


class AppWindow(QWidget):
    def __init__(self):
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

        test_button = QPushButton("Test - no login", self)
        test_button.setGeometry(140, 240, 200, 50)
        test_button.setStyleSheet(button_style)

        login_button = QPushButton("Login - not implemented", self)
        login_button.setGeometry(380, 240, 200, 50)
        login_button.setStyleSheet(button_style)

        send_message_button = QPushButton("Send Message - not implemented", self)
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

        # TODO:
        #  Create pages for file exchange and for message exchange:
        #  - add field for message content, radio buttons for encoding
        #  - add radio fields for encoding type
        #  - add send buttons
        #  - add file browsing

        # Button press handlers
        def test_button_pressed():
            # hide all visible widgets and unhide all widgets for the message selection
            label.hide()
            key_field.hide()
            test_button.hide()
            login_button.hide()

            send_message_button.show()
            send_file_button.show()
            logout_button.show()

            pass

        def login_button_pressed():
            # TODO: Add login functionality
            pass

        def logout_button_pressed():
            # hide all visible widgets and unhide all widgets for the login screen
            label.show()
            key_field.show()
            test_button.show()
            login_button.show()

            send_message_button.hide()
            send_file_button.hide()
            logout_button.hide()

            pass

        def send_message_button_pressed():
            # TODO: Add message sending functionality
            pass

        def send_file_button_pressed():
            # TODO: Add file sending functionality
            pass

        # Connect the button press handlers to the buttons
        test_button.clicked.connect(test_button_pressed)
        login_button.clicked.connect(login_button_pressed)
        logout_button.clicked.connect(logout_button_pressed)
        send_message_button.clicked.connect(send_message_button_pressed)
        send_file_button.clicked.connect(send_file_button_pressed)


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle('Fusion')

    window = AppWindow()

    window.show()
    app.exec_()
