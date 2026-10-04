from PyQt6.QtWidgets import (
    QWizardPage, QComboBox,
    QFormLayout, QLabel,
    QHBoxLayout, QSpinBox,
    QCheckBox
)

from PyQt6.QtCore import Qt

class PageDevices(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Additional Devices")

        self.clayout = QFormLayout()

        vlabel = QLabel("Video")
        vlabel.setStyleSheet("font-weight: bold; font-size: 10pt;")
        self.clayout.addRow(vlabel)

        self.video = QComboBox()
        self.video.addItems(["virtio", "qxl", "std", "vmware", "cirrus"])
        self.video.setCurrentIndex(2) # std as default
        self.clayout.addRow("    Model:", self.video)

        self.connconfig = QHBoxLayout()

        alabel = QLabel("Audio")
        alabel.setStyleSheet("font-weight: bold; font-size: 10pt;")
        self.clayout.addRow(alabel)

        self.audio = QComboBox()
        self.audio.addItems(["None", "ac97", "adlib", "cs4231a", "es1370", "gus", "hda", "sb16", "virtio"])
        self.clayout.addRow("    Model", self.audio)

        self.setLayout(self.clayout)

    def get_data(self):
        return {
            "audio": self.audio.currentText(),
            "video": {
                "model": self.video.currentText(),
                "connection": "QEMU"
            }
        }