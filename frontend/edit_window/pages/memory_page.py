from PyQt6.QtWidgets import QWidget, QFormLayout, QHBoxLayout
from gui.memorybar import MemoryBar

class MemoryPage(QWidget):
    def __init__(self, vm_config):
        super().__init__()

        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        
        self.memory = MemoryBar()
        self.memory.setValue(vm_config.get("memory", 1))

        layout.addRow("Memory (MB):", self.memory)

        self.setLayout(layout)

    def get_data(self):
        return {
            "memory": self.memory.slider.value()
        }