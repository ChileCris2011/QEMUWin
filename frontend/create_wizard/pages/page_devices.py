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

        self.video_connection = QComboBox()
        self.video_connection.addItems(["QEMU", "VNC"])
        self.video_connection.currentTextChanged.connect(self._handle_conn_change)
        self.clayout.addRow("    Connection type:", self.video_connection)

        self.connconfig = QHBoxLayout()
        
        self.vnc_port = QSpinBox()
        self.vnc_port.setRange(5900, 65535) # A little much, I know...
        self.connconfig.addWidget(self.vnc_port)

        self.auto_port = QCheckBox("Auto Port")
        self.auto_port.checkStateChanged.connect(self._handle_auto_change)
        self.connconfig.addWidget(self.auto_port)

        self.clayout.addRow("    VNC Port:", self.connconfig)
        self.clayout.setRowVisible(self.connconfig, False)

        self.clayout.addRow(QLabel("")) # just a simple spacer

        alabel = QLabel("Audio")
        alabel.setStyleSheet("font-weight: bold; font-size: 10pt;")
        self.clayout.addRow(alabel)

        self.audio = QComboBox()
        self.audio.addItems(["None", "ac97", "adlib", "cs4231a", "es1370", "gus", "hda", "sb16", "virtio"])
        self.clayout.addRow("    Model", self.audio)

        self.setLayout(self.clayout)

    def _handle_auto_change(self):
        if self.auto_port.checkState() == Qt.CheckState.Checked:
            self.vnc_port.setEnabled(False)
        else:
            self.vnc_port.setEnabled(True)

    def _handle_conn_change(self):
        if self.video_connection.currentText() == "QEMU":
            self.clayout.setRowVisible(self.connconfig, False)
        else:
            self.clayout.setRowVisible(self.connconfig, True)

    def get_data(self):
        return {
            "audio": self.audio.currentText(),
            "video": {
                "model": self.video.currentText(),
                "connection": self.video_connection.currentText(),
                "port": -1 if self.auto_port.checkState() == Qt.CheckState.Checked else self.vnc_port.value()
            }
        }