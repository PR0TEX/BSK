from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel


class CustomDialog(QDialog):

    def __init__(self, dialog_type="ok"):
        super().__init__()

        self.setWindowTitle("Error!")

        if dialog_type == "yes_no":
            QBtn = QDialogButtonBox.Yes | QDialogButtonBox.No
        else:
            QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.message = QLabel("Dialog message")
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def set_message(self, message_content):
        self.message.setText(message_content)

    def set_title(self, title):
        self.setWindowTitle(title)
