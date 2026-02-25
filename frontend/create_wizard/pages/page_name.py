from PyQt6.QtWidgets import QWizardPage, QVBoxLayout, QLabel, QLineEdit, QComboBox

class PageName(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Virtual Machine Name")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("VM Name:"))
        self.name_line_edit = QLineEdit()
        layout.addWidget(self.name_line_edit)

        layout.addWidget(QLabel("Machine Type:"))
        self.machine_combo = QComboBox()
        self.machine_combo.addItems(["q35", "pc-i440fx"])
        layout.addWidget(self.machine_combo)

        layout.addWidget(QLabel("Firmware:"))
        self.firmware_combo = QComboBox()
        self.firmware_combo.addItems(["BIOS", "UEFI"])
        layout.addWidget(self.firmware_combo)

        self.setLayout(layout)

    def validatePage(self):
        name = self.name_line_edit.text()
        return bool(name.strip())

    def get_data(self):
        return {
            "name": self.name_line_edit.text(),
            "machine": self.machine_combo.currentText(),
            "firmware": self.firmware_combo.currentText()
        }