from PyQt6.QtWidgets import (
    QWidget, QFormLayout,
    QLineEdit, QPushButton,
    QComboBox, QFileDialog,
    QHBoxLayout, QMessageBox
)

class NewMediaPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QFormLayout()

        self.type = QComboBox()
        self.type.addItem("CD-ROM")
        self.type.addItem("Floppy")
        self.type.setCurrentText("CD-ROM")

        self.type.currentTextChanged.connect(self.manage_change)

        self.path = QLineEdit("Empty")

        browse = QPushButton("Browse")
        browse.clicked.connect(self.select_file)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path)
        path_layout.addWidget(browse)

        self.bus = QComboBox()
        self.bus.addItems(["virtio", "sata", "ide", "scsi"])
        self.bus.setCurrentText("virtio")

        self.fake_bus = QComboBox()
        self.fake_bus.addItem("fdc")
        self.fake_bus.setDisabled(True)

        layout.addRow("Type:", self.type)
        layout.addRow("Path:", path_layout)
        layout.addRow("Bus:", self.bus)
        layout.addRow("Bus:", self.fake_bus)
        layout.setRowVisible(3, False)

        self.setLayout(layout)
    
    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Disk")
        if path:
            self.path.setText(path)
        else:
            self.path.setText("Empty")
            # Is it possible to not select a file in a file picker?

    def manage_change(self):
        layout = self.layout()
        if self.type.currentText() == "Floppy":
            layout.setRowVisible(2, False)
            layout.setRowVisible(3, True)
        else:
            layout.setRowVisible(3, False)
            layout.setRowVisible(2, True)

    def get_data(self):
        if self.type.currentText() == "CD-ROM":
            return {
                "type": "CD-ROM",
                "path": self.path.text(),
                "bus": self.bus.currentText()
            }
        else:
            return {
                "type": "Floppy",
                "path": self.path.text()
            }