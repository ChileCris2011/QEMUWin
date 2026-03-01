from PyQt6.QtWidgets import (
    QWidget, QFormLayout,
    QLabel, QLineEdit,
    QHBoxLayout, QVBoxLayout,
    QFileDialog, QPushButton,
    QMessageBox
)

import subprocess, logging

from gui.settings_pages.dialogs.test_window import TestDialog

class QEMUPathPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QFormLayout()

        title = QLabel("QEMU Path (Leave blank to use QEMU in system PATH)")
        title.setStyleSheet("font-size: 12px; font-weight: bold;")

        path_layout = QHBoxLayout()

        self.qemu_folder = QLineEdit()
        path_layout.addWidget(self.qemu_folder)
        browse = QPushButton()
        browse.setText("Browse")

        test_layout = QHBoxLayout()
        test_all = QPushButton()
        test_all.setText("Test all qemu-system")
        test_64 = QPushButton()
        test_64.setText("Test qemu-system-x86_64.exe")

        coming_soon = QPushButton()
        coming_soon.setText("More archs coming soon!")

        #test_32 = QPushButton()
        #test_32.setText("Test qemu-system-i386.exe") <-- Coming soon!
        #test_arm = QPushButton()
        #test_arm.setText("Test qemu-system-arm.exe")

        test_layout.addWidget(test_all)
        test_layout.addWidget(test_64)
        test_layout.addWidget(coming_soon)

        path_layout.addWidget(self.qemu_folder)
        path_layout.addWidget(browse)

        test_all.clicked.connect(self._test_all)
        test_64.clicked.connect(self._test_64)

        browse.clicked.connect(self._browse_folder)

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

        log_pres.addWidget(log_title)
        log_pres.addWidget(log_text)
        log_pres.addLayout(log_buttons)

        layout.addRow(title)
        layout.addRow(path_layout)
        layout.addRow(test_layout)
        layout.addRow(log_pres)

        self.setLayout(layout)
    
    def _test_all(self):
        self._test_64(window=False)
    
    def _test_64(self, window=True):

        cmd = []

        if self.qemu_folder.text():
            cmd += [f"{self.qemu_folder.text()}/qemu-system-x86_64.exe"]
        else:
            cmd += ["qemu-system-x86_64.exe"]
        cmd += ["-version"]

        print(f"Command: {cmd}")

        try:
            command = subprocess.run(cmd, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            logging.debug(command.stdout.decode())
            test_window = TestDialog(0, command.stdout)
            test_window.exec()
        except FileNotFoundError as e:
            test_window = TestDialog(1, e)
            logging.error(f"qemu-system-x86_64.exe could not be found on the specified path")
            test_window.exec()

    def _browse_folder(self):
        path= QFileDialog.getExistingDirectory(
            self,
            "Select the QEMU executable folder"
        )
        if path:
            self.qemu_folder.setText(path)

    def _open_log(self):
        cmd = ["powershell", "-Command", "./latest.log"]
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
    
    def _open_folder(self):
        cmd = ["explorer", "."]
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
    
    def get_data(self):
        return {
            "qemu_path": self.qemu_folder.text()
        }
