from PyQt6.QtWidgets import QWidget, QFormLayout, QComboBox


class NetworkPage(QWidget):
    def __init__(self, config: list):
        super().__init__()

        layout = QFormLayout()

        self.type = QComboBox()
        self.type.addItems(["User (NAT)", "Bridged", "TAP", "None"])
        self.type.setCurrentText(config.get("type"))

        self.model = QComboBox()
        self.model.addItems([
            "e1000",
            "igb",
            "ne2k_pci",
            "pcnet",
            "rocker",
            "rtl8139",
            "tulip",
            "usb-net",
            "virtio-net-pci",
            "vmxnet3"
        ])
        self.model.setCurrentText(config.get("model"))

        layout.addRow("Mode:", self.type)
        layout.addRow("Model:", self.model)

        self.setLayout(layout)

    def get_data(self):
        return {
            "network": "network",
            "type": self.type.currentText(),
            "model": self.model.currentText()
        }
