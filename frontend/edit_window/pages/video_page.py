from PyQt6.QtWidgets import QWidget, QFormLayout, QComboBox, QSpinBox, QHBoxLayout, QLabel, QCheckBox
from PyQt6.QtCore import Qt

class VideoPage(QWidget):
    def __init__(self, config):
        super().__init__()

        layout = QFormLayout()

        self.model = QComboBox()
        self.model.addItems(["virtio", "qxl", "std", "vmware", "cirrus"])
        self.model.setCurrentText(config.get("model", "std"))

        layout.addRow("Video Model:", self.model)

        self.setLayout(layout)

    def get_data(self):
        return {
            "video": {
                "model": self.model.currentText(),
                "connection": "QEMU"
            }
        }
