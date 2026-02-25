from PyQt6.QtWidgets import QWidget, QFormLayout, QSpinBox, QComboBox


class CpuPage(QWidget):
    def __init__(self, vm_config):
        super().__init__()

        layout = QFormLayout()

        cpu = vm_config.get("cpu", {})

        self.model = QComboBox()
        self.model.addItems(["host", "qemu64", "max"])

        self.sockets = QSpinBox()
        self.sockets.setRange(1, 8)

        self.cores = QSpinBox()
        self.cores.setRange(1, 64)

        self.threads = QSpinBox()
        self.threads.setRange(1, 8)

        self.model.setCurrentText(cpu.get("model", "host"))
        #self.sockets.setValue(cpu.get("sockets", 1))
        self.cores.setValue(cpu.get("cores", 2))
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