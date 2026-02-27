
# Pages
from PyQt6.QtWidgets import QWizard
from frontend.create_wizard.pages.page_name import PageName
from frontend.create_wizard.pages.page_install import PageInstall
from frontend.create_wizard.pages.page_cpu_memory import PageCpuMemory
from frontend.create_wizard.pages.page_storage import PageStorage
from frontend.create_wizard.pages.page_network import PageNetwork
from frontend.create_wizard.pages.page_devices import PageDevices
from frontend.create_wizard.pages.page_summary import PageSummary

from backend.vm_manager import VMManager

from gui.styles import APP_STYLE


class CreateVMWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Create New Virtual Machine")
        self.resize(720, 520)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

        self.vm_config = {}
        self.vm_manager = VMManager()

        self.addPage(PageName(self))
        self.addPage(PageInstall(self))
        self.addPage(PageCpuMemory(self))
        self.addPage(PageStorage(self))
        self.addPage(PageNetwork(self))
        self.addPage(PageDevices(self))
        self.addPage(PageSummary(self))

    def accept(self):
        self.vm_config = self.collect_config()

        self.vm_manager.create_vm(self.vm_config["name"], self.vm_config)

        super().accept()

    def collect_config(self):
        config = {}
        for i in range(self.pageIds().__len__()):
            page = self.page(i)
            if hasattr(page, "get_data"):
                config.update(page.get_data())
        return config