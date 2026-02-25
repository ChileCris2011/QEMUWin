from PyQt6.QtWidgets import (
    QWidget, QFormLayout,
    QLineEdit, QPushButton,
    QComboBox, QFileDialog, QHBoxLayout
)


class DiskPage(QWidget):
    def __init__(self, disk_config: dict):
        super().__init__()

        layout = QFormLayout()

        self.path = QLineEdit(disk_config.get("path", ""))

        browse = QPushButton("Browse")
        browse.clicked.connect(self.select_file)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path)
        path_layout.addWidget(browse)

        self.bus = QComboBox()
        self.bus.addItems(["virtio", "sata", "ide", "scsi"])
        self.bus.setCurrentText(disk_config.get("bus"))

        layout.addRow("Path:", path_layout)
        layout.addRow("Bus:", self.bus)

        self.setLayout(layout)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Disk")
        if path:
            self.path.setText(path)

    def get_data(self):
        return {
            "path": self.path.text(),
            "bus": self.bus.currentText()
        }