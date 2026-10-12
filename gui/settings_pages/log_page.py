from PyQt6.QtWidgets import (
    QWidget, QFormLayout,
    QLabel, QLineEdit,
    QHBoxLayout, QVBoxLayout,
    QFileDialog, QPushButton,
    QMessageBox, QComboBox
)

from PyQt6.QtCore import QSettings

import subprocess, logging

from gui.settings_pages.dialogs.test_window import TestDialog

class LogPage(QWidget):
    def __init__(self):
        super().__init__()

        settings = QSettings("QEMUWin", "QEMUWin")

        layout = QFormLayout()

        log_pres = QVBoxLayout()

        log_title = QLabel("QEMUWin logs")
        log_title.setStyleSheet("font-size: 12px; font-weight: bold;")

        log_text = QLabel("QEMUWin keeps a log of events, errors, and debug messages. You can read it to troubleshoot problems with QEMUWin or your VM. It's also necessary if you report a problem on GitHub.", wordWrap=True)

        log_buttons = QHBoxLayout()
        log_open = QPushButton("Open latest.log")
        folder_open = QPushButton("Open installation folder")

        log_open.clicked.connect(self._open_log)
        folder_open.clicked.connect(self._open_folder)

        log_buttons.addWidget(log_open)
        log_buttons.addWidget(folder_open)

        loglevel_title = QLabel("Logging level")
        loglevel_title.setStyleSheet("font-size: 12px; font-weight: bold;")

        loglevel_text = QLabel("The logging file registers messages by level. By default, the INFO level is selected to show general messages. If you need to troubleshoot some error, or need to file a bug, DEBUG level may be necessary.", wordWrap=True)

        loglevel_lay = QHBoxLayout()
        self.logLevels = [50, 40, 30, 20, 10]
        self.loglevel_select = QComboBox()
        self.loglevel_select.addItems(["Critical", "Error", "Warning", "Info", "Debug"])
        self.loglevel_select.setCurrentIndex(self.logLevels.index(settings.value("LogLevel", 20)))
        

        loglevel_lay.addWidget(QLabel("Logging level: "))
        loglevel_lay.addWidget(self.loglevel_select)

        log_pres.addWidget(log_title)
        log_pres.addWidget(log_text)
        log_pres.addLayout(log_buttons)

        log_pres.addWidget(loglevel_title)
        log_pres.addWidget(loglevel_text)
        log_pres.addLayout(loglevel_lay)

        layout.addRow(log_pres)

        self.setLayout(layout)
    
    def _open_log(self):
        cmd = ["powershell", "-Command", "./latest.log"]
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
    
    def _open_folder(self):
        cmd = ["explorer", "."]
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)

    def get_data(self):
        return {
            "log_level": self.logLevels[self.loglevel_select.currentIndex()]
        }
