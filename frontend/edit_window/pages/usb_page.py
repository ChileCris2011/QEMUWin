from PyQt6.QtWidgets import QWidget, QFormLayout, QComboBox


class UsbPage(QWidget):
    def __init__(self, config):
        super().__init__()

        layout = QFormLayout()

        self.model = QComboBox()
        self.model.addItems(["qemu-xhci", "ehci", "uhci"])
        self.model.setCurrentText(config.get("model", "qemu-xhci"))

        layout.addRow("USB Controller:", self.model)

        self.setLayout(layout)

    def get_data(self):
        return {
            "usb": self.model.currentText()
        }