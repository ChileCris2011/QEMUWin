from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton,
    QDialog, QStackedWidget,
    QWidget, QSplitter,
    QListWidgetItem
)
from PyQt6.QtCore import Qt

from gui.settings_pages.qemu_path import QEMUPathPage
from gui.settings_pages.theme_page import ThemePage
from gui.settings_pages.about_page import AboutPage

class SettingsDialog(QDialog):
    def __init__(self, icon_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QEMUWin Settings")
        self.resize(600, 350)
        self.icon_manager = icon_manager
        self.setWindowIcon(self.icon_manager.get_icon("settings"))

        self.pages = []

        self.config = {}

        main_layout = QVBoxLayout()

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.device_list = QListWidget()
        self.device_list.currentRowChanged.connect(self.change_page)

        self.stack = QStackedWidget()

        splitter.addWidget(self.device_list)
        splitter.addWidget(self.stack)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.accept_button = QPushButton("Accept")
        self.accept_button.clicked.connect(self.accept_changes)

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self.apply_changes)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)

        bottom_layout.addWidget(self.accept_button)
        bottom_layout.addWidget(self.apply_btn)
        bottom_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

        self.add_page("QEMU", QEMUPathPage())
        self.add_page("Theme", ThemePage())
        self.add_page("About", AboutPage())

    def add_page(self, name, widget):
        item = QListWidgetItem(name)
        self.device_list.addItem(item)
        self.stack.addWidget(widget)
        self.pages.append(widget)

    def change_page(self, index):
        if index >= 0:
            self.stack.setCurrentIndex(index)

    def accept_changes(self):
        self.apply_changes()
        self.accept()
    
    def apply_changes(self):
        pass