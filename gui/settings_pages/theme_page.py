from PyQt6.QtWidgets import (
    QWidget, QFormLayout,
    QLabel, QComboBox,
)

from PyQt6.QtCore import QSettings

class ThemePage(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = QSettings("QEMUWin", "QEMUWin")

        layout = QFormLayout()

        title = QLabel("Application Theme")
        title.setStyleSheet("font-size: 12px; font-weight: bold;")

        self.theme = QComboBox()
        self.theme.addItems(["Automatic (system)", "Dark", "Light"])

        self.theme_trs = ["auto", "dark", "light"]

        self._mode = self.settings.value("theme/mode")

        self.theme.setCurrentIndex(self.theme_trs.index(f"{self._mode}"))

        layout.addRow(title)
        layout.addRow("Mode:", self.theme)

        self.setLayout(layout)
    
    def get_data(self):
        return {
            "theme": self.theme_trs[self.theme.currentIndex()]
        }