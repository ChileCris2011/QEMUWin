from PyQt6.QtWidgets import QWidget, QFormLayout, QSpinBox


class MemoryPage(QWidget):
    def __init__(self, vm_config):
        super().__init__()

        layout = QFormLayout()

        self.memory = QSpinBox()
        self.memory.setRange(256, 262144)
        self.memory.setValue(vm_config.get("memory", 2048))

        layout.addRow("Memory (MB):", self.memory)

        self.setLayout(layout)

    def get_data(self):
        return {
            "memory": self.memory.value()
        }