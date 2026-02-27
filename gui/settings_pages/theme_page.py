from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout,
    QLabel, QHBoxLayout,
    QHBoxLayout
)

class ThemePage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        layout.addStretch()

        qemuwin_layout = QHBoxLayout()
        qemuwin_layout.addStretch()
        qemuwin = QLabel("QEMUWin")
        qemuwin.setStyleSheet("font-size: 24px; font-weight: bold;")
        qemuwin_layout.addWidget(qemuwin)
        qemuwin_layout.addStretch()

        layout.addLayout(qemuwin_layout)

        layout.addStretch()

        self.setLayout(layout)