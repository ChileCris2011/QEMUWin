from PyQt6.QtWidgets import (
    QWizardPage, QVBoxLayout,
    QPushButton, QListWidget, QLabel
)
from frontend.create_wizard.dialogs.add_media_dialog import AddMediaDialog

from PyQt6.QtCore import Qt

class PageInstall(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Installation Media")

        layout = QVBoxLayout()

        self.media_list = QListWidget()
        layout.addWidget(self.media_list)

        self.toomuchfloppys = QLabel("⚠️ You can add up to 2 Floppy Drives")
        layout.addWidget(self.toomuchfloppys)
        self.toomuchfloppys.hide()

        add_btn = QPushButton("Add Media")
        add_btn.clicked.connect(self.add_media)

        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_media)

        layout.addWidget(add_btn)
        layout.addWidget(remove_btn)

        self.setLayout(layout)

    def add_media(self):
        floppys = len(self.media_list.findItems("[Floppy]", Qt.MatchFlag.MatchStartsWith))
        dialog = AddMediaDialog(floppys < 2, self)
        if dialog.exec():
            data = dialog.get_data()
            display = f"[{data['type']}] {data['path']}"
            self.media_list.addItem(display)
        floppys = len(self.media_list.findItems("[Floppy]", Qt.MatchFlag.MatchStartsWith)) # Yeah, didn't want to create a function
        self.toomuchfloppys.setVisible(floppys >= 2)

    def remove_media(self):
        row = self.media_list.currentRow()
        if row >= 0:
            self.media_list.takeItem(row)

    def get_data(self):
        media = []

        for i in range(self.media_list.count()):
            text = self.media_list.item(i).text()
            type_part = text.split("]")[0][1:]
            path_part = text.split("] ")[1]
            media.append({
                "type": type_part,
                "path": path_part
            })

        return {"media": media}