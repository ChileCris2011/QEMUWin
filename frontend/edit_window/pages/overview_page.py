from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QComboBox


class OverviewPage(QWidget):
    def __init__(self, vm_config):
        super().__init__()

        layout = QFormLayout()

        self.name = QLineEdit(vm_config.get("name", ""))

        self.machine = QComboBox()
        self.machine.addItems(["q35", "pc-i440fx"])
        self.machine.setCurrentText(vm_config.get("machine", "q35"))

        self.firmware = QComboBox()
        self.firmware.addItems(["BIOS", "UEFI"])
        self.firmware.setCurrentText(vm_config.get("firmware", "BIOS"))

        self.boot = QComboBox()
        self.iboot = ["c", "d", "a"]
        self.dboot = ["Hard Drive", "CD-ROM", "Floppy"]
        self.boot.addItems(self.dboot)
        self.boot.setCurrentText(self.dboot[self.iboot.index(vm_config.get("boot", "c"))])

        layout.addRow("Name:", self.name)
        layout.addRow("Machine Type:", self.machine)
        layout.addRow("Firmware:", self.firmware)
        layout.addRow("Boot from:", self.boot)

        self.setLayout(layout)

    def get_data(self):
        return {
            "name": self.name.text(),
            "machine": self.machine.currentText(),
            "firmware": self.firmware.currentText(),
            "boot": self.iboot[self.boot.currentIndex()]
        }