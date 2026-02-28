from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QStyle,
    QTextEdit, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import QSize

class TestDialog(QDialog):
    def __init__(self, code: int, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Test result")
        if code == 0:
            self.resize(200, 200)
        else:
            self.resize(200, 100)

        layout = QVBoxLayout(self)

        message_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        message_layout.addSpacing(24)

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation if code == 0 else QStyle.StandardPixmap.SP_MessageBoxCritical)

        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(QSize(32, 32)))

        message_layout.addWidget(icon_label)

        label = QLabel("Test executed succesfully!" if code == 0 else "Couldn't detect QEMU executable")
        message_layout.addWidget(label)

        message_layout.addSpacing(24)

        layout.addLayout(message_layout)

        if code != 0:
            self.details = QTextEdit()
            self.details.setReadOnly(True)
            self.details.setPlainText(f"{message}")
            self.details.hide()
            layout.addWidget(self.details)

            self.toggle_button = QPushButton("Show details")
            self.toggle_button.clicked.connect(self.toggle_details)
            button_layout.addWidget(self.toggle_button)

            copy_button = QPushButton("Copy message")
            copy_button.clicked.connect(
                lambda: self.details.selectAll() or self.details.copy()
            )
            button_layout.addWidget(copy_button)
        else:
            self.info_title = QLabel("Results:")
            message_list = message.splitlines()
            print(message_list)
            self.info1_cont = QHBoxLayout()
            self.info2_cont = QHBoxLayout()

            self.info1 = QLabel(f"- {message_list[0].decode()}")
            self.info2 = QLabel(f"- {message_list[1].decode()}", wordWrap=True)
            self.info1_cont.addSpacing(8)
            self.info1_cont.addWidget(self.info1)
            self.info2_cont.addSpacing(8)
            self.info2_cont.addWidget(self.info2)
            
            layout.addWidget(self.info_title)
            layout.addLayout(self.info1_cont)
            layout.addLayout(self.info2_cont)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def toggle_details(self):
        if self.details.isVisible():
            self.resize(200, 150)
            self.details.hide()
            self.toggle_button.setText("Show Details")
        else:
            self.resize(200, 300)
            self.details.show()
            self.toggle_button.setText("Hide Details")