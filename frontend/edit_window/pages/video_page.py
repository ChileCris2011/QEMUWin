from PyQt6.QtWidgets import QWidget, QFormLayout, QComboBox


class VideoPage(QWidget):
    def __init__(self, config):
        super().__init__()

        layout = QFormLayout()

        self.model = QComboBox()
        self.model.addItems(["virtio", "qxl", "std", "vmware", "vga", "cirrus"])
        self.model.setCurrentText(config.get("model"))

        layout.addRow("Video Model:", self.model)

        self.setLayout(layout)

    def get_data(self):
        return {
            "video": self.model.currentText()
        }