from PyQt6.QtWidgets import (
    QWizardPage, QVBoxLayout,
    QComboBox
)

class PageNetwork(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Networking")

        layout = QVBoxLayout()

        self.net_type = QComboBox()
        self.net_type.addItems([
            "User (NAT)",
            "Bridged",
            "None"
        ])

        self.net_card = QComboBox()
        self.net_card.addItems([
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

        layout.addWidget(self.net_type)
        layout.addWidget(self.net_card)

        self.net_type.currentIndexChanged.connect(self._select_change)

        self.setLayout(layout)

    def get_data(self):
        return {
            "network":{
                "type": self.net_type.currentText(),
                "model": self.net_card.currentText()
            }
        }
    
    def _select_change(self):
        if self.net_type.currentText() == "None":
            self.net_card.setDisabled(True)
        else:
            self.net_card.setDisabled(False)