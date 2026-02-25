from PyQt6.QtWidgets import QWidget, QFormLayout, QComboBox


class NetworkPage(QWidget):
    def __init__(self, config: list):
        super().__init__()

        print("NetworkPage result:", config)

        layout = QFormLayout()

        self.type = QComboBox()
        self.type.addItems(["User (NAT)", "Bridged", "TAP", "None"])
        self.type.setCurrentText(config.get("type"))

        self.model = QComboBox()
        self.model.addItems(["virtio", "e1000", "rtl8139"])
        self.model.setCurrentText(config.get("model"))

        layout.addRow("Mode:", self.type)
        layout.addRow("Model:", self.model)

        self.setLayout(layout)

    def get_data(self):
        return {
            "type": self.type.currentText(),
            "model": self.model.currentText()
        }
    
# TODO: Add more net cards