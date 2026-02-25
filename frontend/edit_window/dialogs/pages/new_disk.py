from PyQt6.QtWidgets import (
    QWidget, QFormLayout,
    QLineEdit, QPushButton,
    QComboBox, QFileDialog,
    QHBoxLayout, QMessageBox
)

class NewDiskPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QFormLayout()

        self.path= QLineEdit("")

        browse = QPushButton("Browse")
        browse.clicked.connect(self.select_file)

        new_disk = QPushButton("New Disk...")
        browse.clicked.connect(self.new_disk)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path)
        path_layout.addWidget(browse)
        path_layout.addWidget(new_disk)

        self.bus = QComboBox()
        self.bus.addItems(["virtio", "sata", "ide", "scsi"])
        self.bus.setCurrentText("virtio")

        layout.addRow("Path:", path_layout)
        layout.addRow("Bus:", self.bus)

        self.setLayout(layout)
    
    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Disk")
        if path:
            self.path.setText(path)

    def new_disk(self):
        from frontend.create_wizard.dialogs.create_disk_dialog import CreateDiskDialog
        from backend.vm_manager import VMManager

        manager = VMManager()

        create_wizard = CreateDiskDialog(self)
        if create_wizard.exec():
            data = create_wizard.get_data()

            if not data["path"]:
                QMessageBox.warning(self, "Error", "Disk path is required.")
                return

        manager._create_disk_file(data)

        data.pop("mode")
        data.pop("size")
        
        self.path = data["path"]


    def get_data(self):
        return {
            "path": self.path.text(),
            "bus": self.bus.currentText()
        }