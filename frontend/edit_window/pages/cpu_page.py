from PyQt6.QtWidgets import QWidget, QFormLayout, QSpinBox, QComboBox


class CpuPage(QWidget):
    def __init__(self, vm_config):
        super().__init__()

        layout = QFormLayout()

        cpu = vm_config["cpu"]

        self.model = QComboBox()
        self.model.addItems(["athlon", "core2duo", "coreduo", "kvm32", "kvm64", "n270", "pentium", "pentium2", "pentium3", "phenom", "qemu32", "qemu64", "base", "host", "max" , "486", "Broadwell", "Cascadelake-Server", "ClearwaterForest", "Conroe", "Cooperlake", "Denverton", "Dhyana", "EPYC", "EPIC-Genoa", "EPIC-IBPB", "EPYC-Milan", "EPYC-Rome", "EPIC-Turin", "GraniteRapids", "Haswell", "Icelake-Server", "IvyBridge", "KnightsMill", "Nehalem", "Opteron_G1", "Opteron_G2", "Opteron_G3", "Opteron_G4", "Opteron_G5", "Penryn", "SandyBridge", "SapphireRapids", "SierraForest", "Skylake-Client", "Skylake-Server", "Snowridge", "Westmere", "YongFeng"])

        self.sockets = QSpinBox()
        self.sockets.setRange(1, 8)

        self.cores = QSpinBox()
        self.cores.setRange(1, 64)

        self.threads = QSpinBox()
        self.threads.setRange(1, 8)

        self.model.setCurrentText(cpu["model"])
        #self.sockets.setValue(cpu.get("sockets", 1))
        self.cores.setValue(cpu["cores"])
        #self.threads.setValue(cpu.get("threads", 1))

        layout.addRow("Model:", self.model)
        #layout.addRow("Sockets:", self.sockets)
        layout.addRow("Cores:", self.cores)
        #layout.addRow("Threads:", self.threads)

        self.setLayout(layout)

    def get_data(self):
        return {
            "cpu": {
                "model": self.model.currentText(),
#                "sockets": self.sockets.value(),
                "cores": self.cores.value()
#                "threads": self.threads.value()
            }
        }
# TODO: Advanced CPU config for sockets and threads, add more CPU models