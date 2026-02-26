from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QSpinBox,
    QComboBox, QFileDialog, QHBoxLayout,
    QDialogButtonBox
)


class SelectDiskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Virtual Disk")
        self.resize(450, 200)

        layout = QVBoxLayout()
        form = QFormLayout()

        # Path
        self.path_edit = QLineEdit()
        browse = QPushButton("Browse")

        browse.clicked.connect(self.select_path)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse)

        # Bus
        self.bus = QComboBox()
        self.bus.addItems(["virtio", "sata", "ide", "scsi"])

        form.addRow("Path:", path_layout)
        form.addRow("Bus:", self.bus)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

    def select_path(self):
        path = QFileDialog.getOpenFileName(
            self,
            "Disk Location",
            filter="QCOW2 (*.qcow2);;RAW (*.raw)"
        )
        if path:
            self.path_edit.setText(path)

    def get_data(self):
        return {
            "mode": "exixtent",
            "path": self.path_edit.text(),
            "bus": self.bus.currentText()
        }