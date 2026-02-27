from PyQt6.QtWidgets import (
    QWidget, QFormLayout,
    QLabel, QLineEdit,
    QHBoxLayout, QPushButton,
    QFileDialog
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

        layout.addRow(title)
        layout.addRow(path_layout)
        layout.addRow(test_layout)

        test_all.clicked.connect(self._test_all)
        test_64.clicked.connect(self._test_64)

        browse.clicked.connect(self._browse_folder)

        self.setLayout(layout)
    
    def _test_all(self):
        self._test_64(window=False)
    
    def _test_64(self, window=True):
        if self.qemu_folder.text():
            cmd = self.qemu_folder.text().split()
        else:
            cmd = ["qemu-system-x86_64.exe"]
        cmd += ["-version"]

        command = subprocess.run(cmd, capture_output=True)

        if command.returncode != 0:
            logging.error(command.stderr)
            logging.error(command.stdout.decode())
        else:
            logging.debug(command.stdout.decode())
        
        test_window = TestDialog(command.returncode, command.stdout)
        test_window.exec()

    def _browse_folder(self):
        path= QFileDialog.getExistingDirectory(
            self,
            "Select the QEMU executable folder"
        )
        if path:
            self.qemu_folder.setText(path)
    
    def get_data(self):
        return {
            "qemu_path": self.qemu_folder.text()
        }
