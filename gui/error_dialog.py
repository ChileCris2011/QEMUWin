from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QStyle,
    QTextEdit, QPushButton, QHBoxLayout
)
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QFont

class ErrorDialog(QDialog):
    def __init__(self, message, details):
        super().__init__()
        self.setWindowTitle("An error has ocurred")
        self.resize(200, 130)

        layout = QVBoxLayout(self)

        message_layout = QHBoxLayout()

        message_layout.addStretch()

        error_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)

        error_label = QLabel()
        error_label.setPixmap(error_icon.pixmap(QSize(32, 32)))

        message_layout.addWidget(error_label)
        message_layout.addSpacing(8)

        label = QLabel(f"<b>Error:</b> {message}")
        message_layout.addWidget(label)

        message_layout.addStretch()

        layout.addLayout(message_layout)

        self.report_label = QLabel("You can report this error opening a Github Issue")
        layout.addWidget(self.report_label)

        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlainText(details)
        self.details.setFont(QFont("Consolas"))
        self.details.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.details.hide()
        layout.addWidget(self.details)

        button_layout = QHBoxLayout()

        self.toggle_button = QPushButton("Show details")
        self.toggle_button.clicked.connect(self.toggle_details)
        button_layout.addWidget(self.toggle_button)

        copy_button = QPushButton("Copy message")
        copy_button.clicked.connect(
            lambda: self.details.selectAll() or self.details.copy()
        )
        button_layout.addWidget(copy_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def toggle_details(self):
        if self.details.isVisible():
            self.resize(200, 130)
            self.details.hide()
            self.toggle_button.setText("Show Details")
        else:
            self.resize(500, 300)
            self.details.show()
            self.toggle_button.setText("Hide Details")