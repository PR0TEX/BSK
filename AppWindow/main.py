from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCS Project - Encrypted Data Transmission")
        self.setWindowIcon(QIcon("path/to/favicon.png"))
        self.setFixedSize(720, 540)  # make the window non-resizable and 4:3 aspect ratio
        self.setStyleSheet("background-color: #2c2f33;")  # set the background color to a shade of gray

        # Create the widgets
        label = QLabel(self)
        label.setText('Enter a key:')
        label.setFont(QFont('Tahoma', 15))
        label.setAlignment(Qt.AlignCenter)
        label.setGeometry(0, 100, 720, 30)

        key_field = QLineEdit(self)
        key_field.setGeometry(140, 160, 440, 50)  # set the position and size of the key_field widget
        key_field.setStyleSheet("background-color: #ffffff; color: #2c2f33; border-radius: 10px; font-family: Arial; font-size: 16px;")  # set the style of the key_field widget

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

        test_button = QPushButton("Test", self)
        test_button.setGeometry(140, 240, 200, 50)  # set the position and size of the button1 widget
        test_button.setStyleSheet(button_style)

        login_button = QPushButton("Login", self)
        login_button.setGeometry(380, 240, 200, 50)  # set the position and size of the button2 widget
        login_button.setStyleSheet(button_style)  # set the style of the button2 widget

        send_message_button = QPushButton("Send Message", self)
        send_message_button.setGeometry(140, 240, 200, 50)  # set the position and size of the button1 widget
        send_message_button.setStyleSheet(button_style)
        send_message_button.hide()

        send_file_button = QPushButton("Send Message", self)
        send_file_button.setGeometry(140, 240, 200, 50)  # set the position and size of the button1 widget
        send_file_button.setStyleSheet(button_style)
        send_file_button.hide()

        logout_button = QPushButton("Send Message", self)
        logout_button.setGeometry(140, 240, 200, 50)  # set the position and size of the button1 widget
        logout_button.setStyleSheet(button_style)
        logout_button.hide()

        # Create the button press handlers
        def test_button_pressed():
            # hide all existing widgets and unhide all widgets for the message selection
            label.hide()
            test_button.hide()



            pass

        def login_button_pressed():
            # TODO: Add code for handling button 2 press
            pass

        # Connect the button press handlers to the buttons
        test_button.clicked.connect(test_button_pressed)
        login_button.clicked.connect(login_button_pressed)


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle('Fusion')

    # Create the main window
    window = AppWindow()

    # Show the window
    window.show()
    app.exec_()
