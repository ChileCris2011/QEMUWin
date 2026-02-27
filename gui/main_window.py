from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QApplication,
    QPushButton, QHBoxLayout, QLabel, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

from frontend.create_wizard.create_vm_wizard import CreateVMWizard
from frontend.edit_window.edit_vm_window import EditVMWindow

from backend.config_manager import ConfigManager

from gui.vm_list_widget import VMListWidget
from gui.theme_manager import IconManager, ThemeManager
from gui.settings import SettingsDialog

import logging

class MainWindow(QMainWindow):

    vm_state_changed = pyqtSignal(str, object)

    def __init__(self, manager, app=QApplication):
        super().__init__()
        self.manager = manager

        self.app = app

        self.icon_manager = IconManager(mode="dark", app=self.app)

        self.setWindowTitle("QEMU Manager")
        self.resize(800, 500)

        self._build_ui()

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

        self.btn_new = QPushButton("New")
        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.btn_kill = QPushButton("Kill")
        self.btn_edit = QPushButton("Edit")
        self.btn_delete = QPushButton("Delete")
        self.btn_config = QPushButton("Settings")

        self.btn_new.setIcon(self.icon_manager.get_icon("new_window"))
        self.btn_start.setIcon(self.icon_manager.get_icon("play_arrow"))
        self.btn_stop.setIcon(self.icon_manager.get_icon("stop"))
        self.btn_kill.setIcon(self.icon_manager.get_icon("close"))
        self.btn_edit.setIcon(self.icon_manager.get_icon("edit"))
        self.btn_delete.setIcon(self.icon_manager.get_icon("delete"))
        self.btn_config.setIcon(self.icon_manager.get_icon("settings"))

        toolbar_layout.addWidget(self.btn_new)
        toolbar_layout.addWidget(self.btn_start)
        toolbar_layout.addWidget(self.btn_stop)
        toolbar_layout.addWidget(self.btn_kill)
        toolbar_layout.addWidget(self.btn_edit)
        toolbar_layout.addWidget(self.btn_delete)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_config)


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
        self.btn_stop.clicked.connect(self._kill)
        self.btn_edit.clicked.connect(self._edit_vm)
        self.btn_delete.clicked.connect(self._delete_vm)
        self.btn_config.clicked.connect(self._open_config)

        self._update_buttons()

    def _start(self):
        name = self.vm_list.get_selected()
        if name:
            self.manager.start_vm(name)
            logging.info(f"Starting {name}")
        else:
            logging.warning("Tried to start a VM, but no VM was selected")

    def _stop(self):
        name = self.vm_list.get_selected()
        if name:
            if self.manager.get_state(name).value != "stopped":
                self.manager.stop_vm(name)
                logging.info(f"Sending shutdown signal to {name}")
            else:
                logging.warning(f"Tried to send shutdown signal to VM {name}, but it is not started")
        else:
            logging.warning(f"Tried to send shutdown signal to a VM but no VM was selected")

    def _kill(self):
        name = self.vm_list.get_selected()
        if name:
            if self.manager.get_state(name).value != "stopped":
                logging.info(f"Quitting {name} process")
                self.manager.kill_vm(name)
            else:
                logging.warning(f"Tried to quit VM {name}, but it is not started")
        else:
            logging.warning("Tried to quit a VM but no VM was selected")

    def _new_vm(self):
        wizard = CreateVMWizard()
        if wizard.exec():
            self.vm_list.refresh()


    def _edit_vm(self):
        name = self.vm_list.get_selected()
        if not name:
            return
        
        config = ConfigManager()
         
        self.edit_window = EditVMWindow(config.load_vm(name), self.vm_list)
        
        self.edit_window.show()

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
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.manager.delete_vm(name)
                self.vm_list.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _open_config(self):
        settings_dialog = SettingsDialog(self.icon_manager)
        if settings_dialog.exec():
            pass

    def _backend_state_changed(self, name, state):
        self.vm_state_changed.emit(name, state)
        self._update_buttons()


    def _update_vm_ui(self, name, state):
        self.vm_list.update_vm_state(name, state.value)

    def _update_buttons(self):
        name = self.vm_list.get_selected()

        if not name:
            self.btn_start.setDisabled(True)
            self.btn_stop.setDisabled(True)
            self.btn_kill.setDisabled(True)
            self.btn_edit.setDisabled(True)
            self.btn_delete.setDisabled(True)
            return

        state = self.manager.get_state(name)

        self.btn_start.setDisabled(state.value == "running")
        self.btn_stop.setDisabled(state.value != "running")
        self.btn_kill.setDisabled(state.value != "running")
        self.btn_edit.setDisabled(state.value != "stopped")
        self.btn_delete.setDisabled(state.value != "stopped")