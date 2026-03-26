from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QApplication,
    QScrollArea, QMenu
)
from PyQt6.QtGui import QAction

from PyQt6.QtCore import pyqtSignal, QSize, Qt
from qvncwidget6 import QVNCWidget

from gui.theme_manager import IconManager

import sys, threading

class VNCWindow(QMainWindow):
    def __init__(self, config, process, app=QApplication):
        super().__init__()

        self.setWindowTitle(f"{config["name"]} - VNC Viewer")
        self.resize(800, 600)

        self.app = app

        self.oppened = True
        self.resize_window = False

        self.icons = IconManager(app=self.app)

        central = QWidget()
        main_layout = QVBoxLayout(central)

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

        self.disk_btn = {}
        self.floppy_btn = {}
        
        if config.get("media"):
            print(config.get("media"))
            for media in config.get("media"):
                print(media["type"])

                if media["type"] == "CD-ROM":
                    disk_num = media["id"]
                    self.disk_btn[disk_num] = QPushButton()
                    if disk_num < 9:
                        self.disk_btn[disk_num].setIcon(self.icons.get_icon(f"disk_{disk_num}"))
                    else:
                        self.disk_btn[disk_num].setIcon(self.icons.get_icon("disk_plus"))
                    self.disk_btn[disk_num].setToolTip(f"CD-ROM {disk_num}")
                    menu.addWidget(self.disk_btn[disk_num])

                elif media["type"] == "Floppy":
                    flop_num = media["id"]
                    self.floppy_btn[flop_num] = QPushButton()
                    self.floppy_btn[flop_num].setIcon(self.icons.get_icon(f"floppy_{flop_num}")) # QEMU doesn't accepts more than 2 floppy drives, so no need to verify
                    self.floppy_btn[flop_num].setToolTip(f"Floppy {flop_num}")
                    menu.addWidget(self.floppy_btn[flop_num])

        print(self.disk_btn)
        print(self.floppy_btn)

        menu.addStretch()

        size_options = QPushButton()
        size_options.setIcon(self.icons.get_icon("size"))
        size_options.setToolTip("Resize options")

        size_menu = QMenu()

        self.follow_window = QAction("    Resize to Window", self)
        self.follow_window.triggered.connect(self._follow_window)

        size_menu.addAction(self.follow_window)

        size_options.setMenu(size_menu)

        menu.addWidget(size_options)

        main_layout.addLayout(menu)

        self.viewer_container = QScrollArea()
        self.viewer_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.viewer_widget = QWidget()
        
        self.viewer_layout = QHBoxLayout(self.viewer_widget)
        
        self.viewer = QVNCWidget(
            parent=self.viewer_widget,
            host="127.0.0.1", port=config["video"]["port"],
            readOnly=True,
            autoResize=True
        )

        self.viewer_layout.addWidget(self.viewer)

        self.viewer_container.setWidget(self.viewer_widget)
        self.viewer_container.setWidgetResizable(True)

        main_layout.addWidget(self.viewer_container)

        self.viewer.start()

        self.setCentralWidget(central)

    def _follow_window(self):
        if self.resize_window:
            self.resize_window = False
            self.follow_window.setText("    Resize to window")
            self.viewer.setMinimumSize(1, 1)
        else:
            self.resize_window = True
            self.follow_window.setText(" ✔  Resize to window")
            # TODO: Implement change

    def closeEvent(self, ev):
        try:
            self.oppened = False
            self.close()
            self.viewer.stop()
            return super().closeEvent(ev)
        except OSError:
            pass