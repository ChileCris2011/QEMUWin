from PyQt6.QtWidgets import QWidget, QFormLayout, QComboBox


class AudioPage(QWidget):
    def __init__(self, config):
        super().__init__()

        layout = QFormLayout()

        self.model = QComboBox()
        self.model.addItems(["None", "ac97", "adlib", "cs4231a", "es1370", "gus", "hda", "sb16", "virtio"])
        self.model.setCurrentText(config.get("model"))

        layout.addRow("Audio Device:", self.model)

        self.setLayout(layout)

    def get_data(self):
        return {
            "audio": self.model.currentText()
        }