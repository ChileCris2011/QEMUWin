from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QStackedWidget,
    QPushButton, QSplitter, QListWidgetItem,
    QMessageBox
)
from PyQt6.QtCore import Qt

# Pages
from frontend.edit_window.pages.overview_page import OverviewPage
from frontend.edit_window.pages.cpu_page import CpuPage
from frontend.edit_window.pages.memory_page import MemoryPage
from frontend.edit_window.pages.disk_page import DiskPage
from frontend.edit_window.pages.cdrom_page import CdromPage
from frontend.edit_window.pages.floppy_page import FloppyPage
from frontend.edit_window.pages.network_page import NetworkPage
from frontend.edit_window.pages.audio_page import AudioPage
from frontend.edit_window.pages.video_page import VideoPage
from frontend.edit_window.pages.usb_page import UsbPage
from frontend.edit_window.pages.args_page import ArgsPage

# Add device dialog
from frontend.edit_window.dialogs.add_device_dialog import AddDeviceDialog

import copy

class EditVMWindow(QMainWindow):
    def __init__(self, vm_config, vm_list):
        super().__init__()

        self.setWindowTitle(f"Edit VM - {vm_config.get('name', '')}")
        self.resize(800, 550)

        self.original_config = vm_config
        self.vm_config = copy.deepcopy(vm_config)

        self.vm_list = vm_list

        self.pages = []

        central = QWidget()
        main_layout = QVBoxLayout()

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel
        self.device_list = QListWidget()
        self.device_list.currentRowChanged.connect(self.change_page)

        # Right panel
        self.stack = QStackedWidget()

        splitter.addWidget(self.device_list)
        splitter.addWidget(self.stack)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

        # Bottom bar
        bottom_layout = QHBoxLayout()

        self.add_device_btn = QPushButton("+ Add Hardware")
        self.add_device_btn.clicked.connect(self.add_device)

        bottom_layout.addWidget(self.add_device_btn)
        bottom_layout.addStretch()

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self.apply_changes)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)

        bottom_layout.addWidget(self.apply_btn)
        bottom_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(bottom_layout)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        self.build_pages()

    def build_pages(self):

        # Core
        self.add_page("Overview", OverviewPage(self.vm_config))
        self.add_page("CPU", CpuPage(self.vm_config))
        self.add_page("Memory", MemoryPage(self.vm_config))

        # Storage
        if self.vm_config.get("storage"):
            for i, disk in enumerate(self.vm_config.get("storage")):
                self.add_page(f"Disk {i+1}", DiskPage(disk))

        # CDROM
        if self.vm_config.get("media"):
            num = 0
            for i, media in enumerate(self.vm_config.get("media")):
                if media.get("type") == "CD-ROM":
                    num += 1
                    self.add_page(f"CD-ROM {num}", CdromPage(media))
        
        # Floppy
        if self.vm_config.get("media"):
            num = 0
            for i, media in enumerate(self.vm_config.get("media")):
                if media.get("type") == "Floppy":
                    num += 1
                    self.add_page(f"Floppy {num}", FloppyPage(media))

        # Network
        if self.vm_config.get("network"):
            for i, net in enumerate(self.vm_config.get("network")):
                self.add_page(f"NIC {i+1}", NetworkPage(net))

        # Audio
        if self.vm_config.get("audio"):
            self.add_page("Sound", AudioPage(
                {"model": self.vm_config.get("audio")}
            ))

        # Video
        if self.vm_config.get("video"):
            self.add_page("Video", VideoPage(
                {"model": self.vm_config.get("video")}
            ))

        # USB
        if self.vm_config.get("usb"):
            self.add_page("USB Controller", UsbPage(
                {"model": self.vm_config.get("usb")}
            ))
        
        # Qargs
        self.add_page("QEMU args", ArgsPage(self.vm_config))

    def add_page(self, name, widget):
        item = QListWidgetItem(name)
        self.device_list.addItem(item)
        self.stack.addWidget(widget)
        self.pages.append(widget)

    def change_page(self, index):
        if index >= 0:
            self.stack.setCurrentIndex(index)

    # --------------------------------------------------
    # Add Hardware
    # --------------------------------------------------

    def add_device(self):
        dialog = AddDeviceDialog()
        if dialog.exec():
            device = dialog.get_data()

            match int(device.get("index")):
                case 0:
                    page = DiskPage(device.get("info"))
                    self.add_page("New Disk", page)
                case 1:
                    info = device.get("info")
                    if info.get("type") == "CD-ROM":
                        page = CdromPage(info)
                        self.add_page("New CD-ROM", page)
                    else:
                        page = FloppyPage(info)
                        self.add_page("New Floppy", page)

    # --------------------------------------------------
    # Collect + Apply
    # --------------------------------------------------

    def collect_all_data(self):

        new_config = {}

        storage = []
        media = []
        network = []
        args = []

        for page in self.pages:
            if hasattr(page, "get_data"):
                data = page.get_data()

                if "cpu" in data:
                    new_config["cpu"] = data["cpu"]

                elif "memory" in data:
                    new_config["memory"] = data["memory"]

                elif "disk" in data:
                    data.pop("disk")
                    storage.append(data)

                elif "cdrom" in data:
                    data.pop("cdrom")
                    media.append({
                        "type": "CD-ROM",
                        **data
                    })

                elif "floppy" in data:
                    data.pop("floppy")
                    media.append({
                        "type": "Floppy",
                        **data
                    })

                elif "network" in data:
                    data.pop("network")
                    network.append(data)

                elif "audio" in data:
                    new_config["audio"] = data["audio"]

                elif "video" in data:
                    new_config["video"] = data["video"]

                elif "usb" in data:
                    new_config["usb"] = data["usb"]

                elif "name" in data:
                    new_config.update(data)

                elif "args" in data:
                    for arg in data["args"]:
                        args.append(arg)


        new_config["storage"] = storage
        new_config["media"] = media
        new_config["network"] = network
        new_config["qargs"] = args

        print(f"New config: {new_config["qargs"]}\n\n")

        return new_config

    def apply_changes(self):
        from backend.vm_manager import VMManager

        manager = VMManager()

        self.vm_config = self.collect_all_data()

        manager.edit_vm(self.original_config.get("name"), self.vm_config)

        QMessageBox.information(
            self,
            "Changes Applied",
            "Changes have been applied succesfully"
        )
        
        self.close()

        self.vm_list.refresh()