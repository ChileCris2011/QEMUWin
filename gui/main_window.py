from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QHBoxLayout, QLabel, QMessageBox
)
from PySide6.QtCore import Signal

from frontend.create_wizard.create_vm_wizard import CreateVMWizard
from frontend.edit_window.edit_vm_window import EditVMWindow

from backend.config_manager import ConfigManager

from gui.vm_list_widget import VMListWidget
from gui.styles import APP_STYLE


class MainWindow(QMainWindow):

    vm_state_changed = Signal(str, object)

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

        self.setWindowTitle("QEMU Manager")
        self.resize(800, 500)

        self._build_ui()
        self.setStyleSheet(APP_STYLE)

        self.manager.on_vm_state_changed = self._backend_state_changed
        self.vm_state_changed.connect(self._update_vm_ui)

    def _build_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()

        # Header
        title = QLabel("Virtual Machines")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        self.btn_new = QPushButton("➕ New")
        self.btn_start = QPushButton("▶ Start")
        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_edit = QPushButton("⚙ Edit")
        self.btn_delete = QPushButton("🗑 Delete")

        toolbar_layout.addWidget(self.btn_new)
        toolbar_layout.addWidget(self.btn_start)
        toolbar_layout.addWidget(self.btn_stop)
        toolbar_layout.addWidget(self.btn_edit)
        toolbar_layout.addWidget(self.btn_delete)
        toolbar_layout.addStretch()

        main_layout.addLayout(toolbar_layout)

        # VM List
        self.vm_list = VMListWidget(self.manager)
        main_layout.addWidget(self.vm_list)
        self.vm_list.itemSelectionChanged.connect(self._update_buttons)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        self.btn_new.clicked.connect(self._new_vm)
        self.btn_start.clicked.connect(self._start)
        self.btn_stop.clicked.connect(self._stop)
        self.btn_edit.clicked.connect(self._edit_vm)
        self.btn_delete.clicked.connect(self._delete_vm)

        self._update_buttons()

    def _start(self):
        name = self.vm_list.get_selected()
        if name:
            self.manager.start_vm(name)
            print(f"Starting {name}")
        else:
            print(f"No VM was selected")

    def _stop(self):
        name = self.vm_list.get_selected()
        if name:
            if self.manager.get_state(name).value != "stopped":
                self.manager.stop_vm(name)
                print(f"Sending shutdown signal to {name}")
            else:
                print(f"VM {name} is not started")
        else:
            print(f"No VM was selected")

    def _new_vm(self):
        wizard = CreateVMWizard()
        if wizard.exec():
            self.vm_list.refresh()


    def _edit_vm(self):
        name = self.vm_list.get_selected()
        if not name:
            return
        
        config = ConfigManager()
         
        self.edit_window = EditVMWindow(config.load_vm(name))
        
        if self.edit_window.show():
            self.vm_list.refresh()

    def _delete_vm(self):
        name = self.vm_list.get_selected()
        if not name:
            return

        if self.manager.get_state(name).value != "stopped":
            QMessageBox.warning(
                self,
                "Cannot Delete",
                "Cannot delete a running VM."
            )
            return

        reply = QMessageBox.question(
            self,
            "Delete VM",
            f"Are you sure you want to delete '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.manager.delete_vm(name)
                self.vm_list.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _backend_state_changed(self, name, state):
        self.vm_state_changed.emit(name, state)


    def _update_vm_ui(self, name, state):
        self.vm_list.update_vm_state(name, state.value)

    def _update_buttons(self):
        name = self.vm_list.get_selected()

        if not name:
            self.btn_start.setDisabled(True)
            self.btn_stop.setDisabled(True)
            self.btn_edit.setDisabled(True)
            self.btn_delete.setDisabled(True)
            return

        state = self.manager.get_state(name)

        self.btn_start.setDisabled(state.value == "running")
        self.btn_stop.setDisabled(state.value != "running")
        self.btn_edit.setDisabled(state.value != "stopped")
        self.btn_delete.setDisabled(state.value != "stopped")