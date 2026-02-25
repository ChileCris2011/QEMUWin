from PyQt6.QtWidgets import (
    QWizardPage, QFormLayout,
    QComboBox
)

class PageDevices(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Additional Devices")

        layout = QFormLayout()

        self.audio = QComboBox()
        self.audio.addItems(["None", "ac97", "intel-hda", "ich9-intel-hda", "hda-duplex", "sb16", "es1370", "usb-audio", "virtio-sound"])

        self.video = QComboBox()
        self.video.addItems(["virtio", "qxl", "std", "vmware", "vga", "cirrus"])

        layout.addRow("Audio:", self.audio)
        layout.addRow("Video:", self.video)

        self.setLayout(layout)

    def get_data(self):
        return {
            "audio": self.audio.currentText(),
            "video": self.video.currentText()
        }