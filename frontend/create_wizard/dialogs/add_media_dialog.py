from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QComboBox, QLineEdit, QPushButton,
    QFileDialog, QHBoxLayout, QDialogButtonBox
)


class AddMediaDialog(QDialog):
    def __init__(self, addfloppy, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Installation Media")
        self.resize(400, 150)

        layout = QVBoxLayout()
        self.form = QFormLayout()

        # Media type
        self.media_type = QComboBox()
        self.media_type.addItem("CD-ROM")
        # Block Floppy options if there's already 2
        if addfloppy:
            self.media_type.addItem("Floppy")
        
        self.media_type.currentTextChanged.connect(self._on_media_change)

        # Path
        self.path_edit = QLineEdit()
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_btn)

        # Bus
        self.bus_box = QComboBox()
        self.bus_box.addItems(["virtio", "sata", "ide", "scsi"])
        self.bus_dummy = QComboBox()
        self.bus_dummy.addItem("fdc")
        self.bus_dummy.setDisabled(True)

        self.form.addRow("Media Type:", self.media_type)
        self.form.addRow("File:", path_layout)
        self.form.addRow("Bus:", self.bus_box)
        self.form.addRow("Bus:", self.bus_dummy)
        self.form.setRowVisible(3, False)

        layout.addLayout(self.form)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

    def browse_file(self):
        if self.media_type.currentText() == "Floppy":
            file_filter = "Floppy Images (*.img *.flp)"
        else:
            file_filter = "ISO Images (*.iso)"

        path, _ = QFileDialog.getOpenFileName(self, "Select Media", filter=file_filter)
        if path:
            self.path_edit.setText(path)

    def _on_media_change(self):
        if self.media_type.currentText() == "CD-ROM":
            self.form.setRowVisible(2, True)
            self.form.setRowVisible(3, False)
        else:
            self.form.setRowVisible(3, True)
            self.form.setRowVisible(2, False)

    def get_data(self):
        return {
            "type": self.media_type.currentText(),
            "path": self.path_edit.text() if self.path_edit.text() else "Empty",
            "bus": self.bus_box.currentText() if self.media_type.currentText() == "CD-ROM" else "fdc"
        }

    def accept(self):
        super().accept()