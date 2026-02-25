from PyQt6.QtWidgets import (
    QWidget, QFormLayout,
    QLineEdit, QPushButton,
    QComboBox, QFileDialog, QHBoxLayout
)


class FloppyPage(QWidget):
    def __init__(self, config):
        super().__init__()

        layout = QFormLayout()

        self.path = QLineEdit(config.get("path"))

        browse = QPushButton("Browse")
        browse.clicked.connect(self.select_image)

        eject = QPushButton("Eject")
        eject.clicked.connect(self.eject_media)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path)
        path_layout.addWidget(browse)
        path_layout.addWidget(eject)

        layout.addRow("Media Path:", path_layout)

        self.setLayout(layout)

    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select ISO", filter="ISO (*.iso)")
        if path:
            self.path.setText(path)

    def eject_media(self):
        self.path.setText("Empty")

    def get_data(self):
        return {
            "path": self.path.text()
        }