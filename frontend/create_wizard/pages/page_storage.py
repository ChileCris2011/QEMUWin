from PyQt6.QtWidgets import (
    QWizardPage, QVBoxLayout,
    QPushButton, QListWidget,
    QFileDialog, QMessageBox
)

from frontend.create_wizard.dialogs.create_disk_dialog import CreateDiskDialog


class PageStorage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Storage Configuration")

        self.disks = []

        layout = QVBoxLayout()

        self.disk_list = QListWidget()
        layout.addWidget(self.disk_list)

        self.new_btn = QPushButton("Create New Disk")
        self.new_btn.clicked.connect(self.create_disk)

        self.existing_btn = QPushButton("Use Existing Disk")
        self.existing_btn.clicked.connect(self.add_existing_disk)

        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_selected)

        layout.addWidget(self.new_btn)
        layout.addWidget(self.existing_btn)
        layout.addWidget(self.remove_btn)

        self.setLayout(layout)

    # Create new disk file
    def create_disk(self):
        dialog = CreateDiskDialog(self)
        if dialog.exec():
            data = dialog.get_data()

            if not data["path"]:
                QMessageBox.warning(self, "Error", "Disk path is required.")
                return

            self.disks.append(data)
            self.refresh_list()

    # Select an existing disk file
    def add_existing_disk(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Existing Disk",
            filter="Disk Images (*.qcow2 *.raw *.img)"
        )

        if path:
            disk_data = {
                "mode": "existing",
                "path": path,
                "format": "auto",  # Does it work?
                "bus": "virtio"
            }

            self.disks.append(disk_data)
            self.refresh_list()

    # Remove
    def remove_selected(self):
        row = self.disk_list.currentRow()
        if row >= 0:
            self.disks.pop(row)
            self.refresh_list()

    # Refresh list
    def refresh_list(self):
        self.disk_list.clear()

        for disk in self.disks:
            if disk["mode"] == "create":
                text = (
                    f"[NEW] {disk['path']} | "
                    f"{disk['size']}GB | "
                    f"{disk['format']} | "
                    f"{disk['bus']}"
                )
            else:
                text = f"[EXISTING] {disk['path']}"

            self.disk_list.addItem(text)

    def get_data(self):
        return {
            "storage": self.disks
        }