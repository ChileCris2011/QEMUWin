from PyQt6.QtWidgets import (
    QWidget, QFormLayout,
    QLineEdit, QPushButton,
    QComboBox, QFileDialog, QHBoxLayout
)


class CdromPage(QWidget):
    def __init__(self, config):
        super().__init__()

        layout = QFormLayout()

        self.path = QLineEdit(config.get("path"))

        browse = QPushButton("Browse")
        browse.clicked.connect(self.select_iso)

        eject = QPushButton("Eject")
        eject.clicked.connect(self.eject_media)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path)
        path_layout.addWidget(browse)
        path_layout.addWidget(eject)

        self.bus = QComboBox()
        self.bus.addItems(["sata", "ide", "scsi"])
        self.bus.setCurrentText(config.get("bus"))

        layout.addRow("ISO Path:", path_layout)
        layout.addRow("Bus:", self.bus)

        self.setLayout(layout)

    def select_iso(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select ISO", filter="ISO (*.iso)")
        if path:
            self.path.setText(path)

    def eject_media(self):
        self.path.setText("Empty")

    def get_data(self):
        return {
            "cdrom": "cdrom",
            "path": self.path.text(),
            "bus": self.bus.currentText()
        }