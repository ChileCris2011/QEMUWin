from PyQt6.QtWidgets import QWidget, QFormLayout, QComboBox


class AudioPage(QWidget):
    def __init__(self, config):
        super().__init__()

        layout = QFormLayout()

        self.model = QComboBox()
        self.model.addItems(["None", "AC97", "ICH9", "HDA"])
        self.model.setCurrentText(config.get("model", "None"))

        layout.addRow("Audio Device:", self.model)

        self.setLayout(layout)

    def get_data(self):
        return {
            "audio": self.model.currentText()
        }