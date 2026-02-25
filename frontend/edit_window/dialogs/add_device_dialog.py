from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout,
    QListWidget, QDialogButtonBox
)


class AddDeviceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Hardware")
        self.resize(300, 300)

        layout = QVBoxLayout()

        self.device_list = QListWidget()
        self.device_list.addItems([
            "Disk",
            "CD-ROM",
            "Network",
            "Sound",
            "Video",
            "USB Controller"
        ])

        layout.addWidget(self.device_list)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

    def get_selected_device(self):
        item = self.device_list.currentItem()
        return item.text() if item else None
    
# TODO: Test