from PyQt6.QtWidgets import (
    QWizardPage, QFormLayout,
    QSpinBox, QComboBox
)

class PageCpuMemory(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("CPU and Memory")

        layout = QFormLayout()

        self.cores = QSpinBox()
        self.cores.setRange(1, 64)
        self.cores.setValue(2)

        self.memory = QSpinBox()
        self.memory.setRange(512, 131072)
        self.memory.setValue(2048)

        self.cpu_model = QComboBox()
        self.cpu_model.addItems(["athlon", "core2duo", "coreduo", "kvm32", "kvm64", "n270", "pentium", "pentium2", "pentium3", "phenom", "qemu32", "qemu64", "base", "host", "max" , "486", "Broadwell", "Cascadelake-Server", "ClearwaterForest", "Conroe", "Cooperlake", "Denverton", "Dhyana", "EPYC", "EPIC-Genoa", "EPIC-IBPB", "EPYC-Milan", "EPYC-Rome", "EPIC-Turin", "GraniteRapids", "Haswell", "Icelake-Server", "IvyBridge", "KnightsMill", "Nehalem", "Opteron_G1", "Opteron_G2", "Opteron_G3", "Opteron_G4", "Opteron_G5", "Penryn", "SandyBridge", "SapphireRapids", "SierraForest", "Skylake-Client", "Skylake-Server", "Snowridge", "Westmere", "YongFeng"])
        # Didn't have a better way?

        layout.addRow("CPU Model:", self.cpu_model)
        layout.addRow("Cores:", self.cores)
        layout.addRow("Memory (MB):", self.memory)

        self.setLayout(layout)

    def get_data(self):
        return {
            "cpu": {
                "model": self.cpu_model.currentText(),
                "cores": self.cores.value()
            },
            "memory": self.memory.value()
        }