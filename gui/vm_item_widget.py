from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

class VMItemWidget(QWidget):
    def __init__(self, name, state="stopped", memory="Unknown"):
        super().__init__()

        self.setObjectName("vmCard")

        layout = QVBoxLayout()
        header_layout = QHBoxLayout()

        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.state_label = QLabel(self._state_icon(state) + " " + state.capitalize())

        header_layout.addWidget(self.name_label)
        header_layout.addStretch()
        header_layout.addWidget(self.state_label)

        self.memory_label = QLabel(f"Memory: {memory} MB")

        layout.addLayout(header_layout)
        layout.addWidget(self.memory_label)

        self.setLayout(layout)

    def _state_icon(self, state):
        icons = {
            "stopped": "🔴",
            "starting": "🟡",
            "running": "🟢",
            "paused": "🔵",
            "error": "⚫"
        }
        return icons.get(state, "⚪")

    def update_state(self, state):
        self.state_label.setText(self._state_icon(state) + " " + state.capitalize())