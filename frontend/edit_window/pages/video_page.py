from PyQt6.QtWidgets import QWidget, QFormLayout, QComboBox, QSpinBox, QHBoxLayout, QLabel, QCheckBox
from PyQt6.QtCore import Qt

class VideoPage(QWidget):
    def __init__(self, config):
        super().__init__()

        layout = QFormLayout()

        self.model = QComboBox()
        self.model.addItems(["virtio", "qxl", "std", "vmware", "cirrus"])
        self.model.setCurrentText(config.get("model", "std"))

        layout.addRow("Video Model:", self.model)

        self.connection = QComboBox()
        self.connection.addItems(["QEMU", "VNC"])
        self.connection.setCurrentText(config.get("connection", "QEMU"))
        self.connection.currentTextChanged.connect(self._handle_conn_change)

        layout.addRow("Connection Type:", self.connection)

        connconfig = QHBoxLayout()
        self.conn_label = QLabel("VNC port:")
        connconfig.addWidget(self.conn_label)

        self.vnc_port = QSpinBox()
        self.vnc_port.setRange(5900, 65535)
        connconfig.addWidget(self.vnc_port)

        self.auto_port = QCheckBox("Auto Port")
        self.auto_port.checkStateChanged.connect(self._handle_auto_change)
        connconfig.addWidget(self.auto_port)

        layout.addRow(connconfig)

        self.setLayout(layout)
        self._handle_conn_change()
        self._handle_auto_change()

    def _handle_auto_change(self):
        if self.auto_port.checkState() == Qt.CheckState.Checked:
            self.vnc_port.setEnabled(False)
        else:
            self.vnc_port.setEnabled(True)
    
    def _handle_conn_change(self):
        if self.connection.currentText() == "QEMU":
            self.conn_label.setVisible(False)
            self.vnc_port.setVisible(False)
            self.auto_port.setVisible(False)
        else:
            self.conn_label.setVisible(True)
            self.vnc_port.setVisible(True)
            self.auto_port.setVisible(True)

    def get_data(self):
        if self.connection.currentText == "QEMU":
            return {
                "video": {
                    "model": self.model.currentText(),
                    "connection": self.connection.currentText()
                }
            }
        else:
            return {
                "video": {
                    "model": self.model.currentText(),
                    "connection": self.connection.currentText(),
                    "port": -1 if self.auto_port.checkState() == Qt.CheckState.Checked else self.vnc_port.value()
                }
            }