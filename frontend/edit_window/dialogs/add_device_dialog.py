from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton,
    QDialog, QStackedWidget,
    QWidget, QSplitter, QListWidgetItem
)
from PyQt6.QtCore import Qt

from frontend.edit_window.dialogs.pages.new_disk import NewDiskPage
from frontend.edit_window.dialogs.pages.new_media import NewMediaPage
#from frontend.edit_window.dialogs.pages.new_nic import NewNICPage

class AddDeviceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add hardware")

        self.pages = []

        self.config = {}

        central = QWidget()
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

        self.apply_btn = QPushButton("Add")
        self.apply_btn.clicked.connect(self.apply_changes)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)

        bottom_layout.addWidget(self.apply_btn)
        bottom_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

        self.add_page("Disk", NewDiskPage())
        self.add_page("Media", NewMediaPage())
        #self.add_page("NIC", NewNICPage())

    def add_page(self, name, widget):
        item = QListWidgetItem(name)
        self.device_list.addItem(item)
        self.stack.addWidget(widget)
        self.pages.append(widget)

    def change_page(self, index):
        if index >= 0:
            self.stack.setCurrentIndex(index)

    def apply_changes(self):
        page = self.pages[self.stack.currentIndex()]
        config = {"index": self.stack.currentIndex()}
        config.update({"info": page.get_data()})
        self.config = config
        self.accept()

    def get_data(self):
        return self.config