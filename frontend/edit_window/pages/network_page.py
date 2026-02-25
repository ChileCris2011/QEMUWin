from PyQt6.QtWidgets import QWidget, QFormLayout, QComboBox


class NetworkPage(QWidget):
    def __init__(self, config):
        super().__init__()

        layout = QFormLayout()

        self.type = QComboBox()
        self.type.addItems(["user (NAT)", "bridged", "tap", "none"])
        self.type.setCurrentText(config.get("type", "user (NAT)"))

        self.model = QComboBox()
        self.model.addItems(["virtio", "e1000", "rtl8139"])
        self.model.setCurrentText(config.get("model", "virtio"))

        layout.addRow("Mode:", self.type)
        layout.addRow("Model:", self.model)

        self.setLayout(layout)

    def get_data(self):
        return {
            "type": self.type.currentText(),
            "model": self.model.currentText()
        }
    
# TODO: Add more net cards