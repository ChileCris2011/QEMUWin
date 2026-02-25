from PyQt6.QtWidgets import (
    QWidget, QFormLayout,
    QLineEdit, QPushButton,
    QComboBox, QSpinBox, QFileDialog, QHBoxLayout
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

        self.size = QSpinBox()
        self.size.setRange(1, 2048)
        self.size.setValue(disk_config.get("size", 20))

        self.bus = QComboBox()
        self.bus.addItems(["virtio", "sata", "ide", "scsi"])
        self.bus.setCurrentText(disk_config.get("bus", "virtio"))

        self.format = QComboBox()
        self.format.addItems(["qcow2", "raw"])
        self.format.setCurrentText(disk_config.get("format", "qcow2"))

        layout.addRow("Path:", path_layout)
        layout.addRow("Size (GB):", self.size)
        layout.addRow("Bus:", self.bus)
        layout.addRow("Format:", self.format)

        self.setLayout(layout)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Disk")
        if path:
            self.path.setText(path)

    def get_data(self):
        return {
            "path": self.path.text(),
            "size": self.size.value(),
            "bus": self.bus.currentText(),
            "format": self.format.currentText()
        }