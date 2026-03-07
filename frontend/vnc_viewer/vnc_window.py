from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QScrollArea, QSizePolicy
from PyQt6.QtCore import pyqtSignal, QSize
from qvncwidget6.qvncwidget6 import QVNCWidget

from gui.theme_manager import IconManager

import sys

class VNCWindow(QMainWindow):
    resize = pyqtSignal(QSize)
    def __init__(self, config, process, app=QApplication):
        super().__init__()
        self.setWindowTitle(f"{config["name"]} - VNC Viewer")

        self.app = app

        self.icons = IconManager(app=self.app)

        central = QWidget()
        main_layout = QVBoxLayout()

        menu = QHBoxLayout()

        btn_pause = QPushButton()
        btn_pause.setIcon(self.icons.get_icon("pause"))
        btn_pause.setToolTip("Pause VM")
        menu.addWidget(btn_pause)

        btn_resume = QPushButton()
        btn_resume.setIcon(self.icons.get_icon("play_arrow"))
        btn_resume.setToolTip("Resume VM")
        btn_resume.setEnabled(False)
        menu.addWidget(btn_resume)

        menu.addSpacing(16)

        # Get all media to assign buttons

        disks = 0
        self.disk_btn = {}
        floppys = 0
        self.floppy_btn = {}

        if config.get("media"):
            print(config.get("media"))
            for media in config.get("media"):
                print(media["type"])

                if media["type"] == "CD-ROM":
                    self.disk_btn[disks] = QPushButton()
                    if disks < 9:
                        self.disk_btn[disks].setIcon(self.icons.get_icon(f"disk_{disks+1}"))
                    else:
                        self.disk_btn[disks].setIcon(self.icons.get_icon("disk"))
                    self.disk_btn[disks].setToolTip(f"CD-ROM {disks+1}")
                    menu.addWidget(self.disk_btn[disks])
                    disks += 1

                elif media["type"] == "Floppy":
                    self.floppy_btn[floppys] = QPushButton()
                    self.floppy_btn[floppys].setIcon(self.icons.get_icon(f"floppy_{floppys+1}")) # QEMU doesn't accepts more than 2 floppy drives, so no need to verify
                    self.floppy_btn[floppys].setToolTip(f"Floppy {floppys+1}")
                    menu.addWidget(self.floppy_btn[floppys])
                    floppys += 1

        menu.addStretch()

        main_layout.addLayout(menu)

        self.viewer_container= QScrollArea()
        
        self.viewer = QVNCWidget(
            parent=self,
            host="127.0.0.1", port=config["vnc"],
            readOnly=True
        )
        self.viewer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.viewer_container.setWidget(self.viewer)
        self.viewer_container.setWidgetResizable(True)

        main_layout.addWidget(self.viewer_container)

        self.viewer.onInitialResize.connect(self.resize)
        self.viewer.start()

        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def closeEvent(self, ev):
        try:
            self.close()
            self.viewer.stop()
            return super().closeEvent(ev)
        except OSError:
            pass