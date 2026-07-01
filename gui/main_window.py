from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QApplication,
    QPushButton, QHBoxLayout, QLabel, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import pyqtSignal, Qt

from frontend.create_wizard.create_vm_wizard import CreateVMWizard
from frontend.edit_window.edit_vm_window import EditVMWindow
from frontend.vnc_viewer.vnc_window import VNCWindow

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

        self._update_vm_files()

        self.process = {}
        self.vnc_window = None

        self.icon_manager = IconManager(mode="dark", app=self.app)
        self.theme_manager = ThemeManager(self.app)

        self.setWindowTitle("QEMU Manager")
        self.resize(800, 500)

        self._build_ui()

        self.manager.on_vm_state_changed = self._backend_state_changed
        self.manager.vm_stopped = self._handle_stop
        self.vm_state_changed.connect(self._update_vm_ui)
        self.theme_manager.themeChanged.connect(self._build_ui)

        self.manager.restore_vms()
        logging.info("VMs restored")

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
        #self.btn_refresh = QPushButton("Refresh")
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
        #toolbar_layout.addWidget(self.btn_refresh)
        toolbar_layout.addWidget(self.btn_config)


        main_layout.addLayout(toolbar_layout)

        # VM List
        self.vm_list = VMListWidget(self.manager)
        main_layout.addWidget(self.vm_list)
        self.vm_list.itemSelectionChanged.connect(self._update_buttons)
        self.vm_list.itemDoubleClicked.connect(self._manage_double)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        self.btn_new.clicked.connect(self._new_vm)
        self.btn_start.clicked.connect(self._start)
        self.btn_stop.clicked.connect(self._stop)
        self.btn_kill.clicked.connect(self._kill)
        self.btn_edit.clicked.connect(self._edit_vm)
        self.btn_delete.clicked.connect(self._delete_vm)
        #self.btn_refresh.clicked.connect(self.vm_list.refresh)
        self.btn_config.clicked.connect(self._open_config)

        self._update_buttons()

    def _start(self):
        name = self.vm_list.get_selected()
        if name:
            try:
                self.process.update({name: self.manager.start_vm(name)})
                logging.info(f"Starting {name}")
            except:
                #del self.process[name]
                from backend.vm_state import VMState
                self._update_vm_ui(name, VMState.ERROR)
                logging.error(f"Error starting VM {name}")
                raise
        else:
            logging.warning("Tried to start a VM, but no VM was selected")

    def _stop(self):
        name = self.vm_list.get_selected()
        if name:
            if self.manager.get_state(name).value != "stopped":
                self.manager.stop_vm(name)
                #del self.process[name]
                logging.info(f"Sending shutdown signal to {name}")
            else:
                logging.warning(f"Tried to send shutdown signal to VM {name}, but it is not started")
        else:
            logging.warning(f"Tried to send shutdown signal to a VM but no VM was selected")

    def _kill(self):
        name = self.vm_list.get_selected()
        if name:
            if self.manager.get_state(name).value != "stopped":
                reply = QMessageBox.warning(
                    self,
                    "Kill VM",
                    f"Are you sure you want to force {name} to shut down?\n\nThis can cause data corruption. Only use this if the machine becomes unresponsive.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    logging.info(f"Forcing {name} to shut down")
                    self.manager.kill_vm(name)
                    #del self.process[name]
            else:
                logging.warning(f"Tried to quit VM {name}, but it is not started")
        else:
            logging.warning("Tried to quit a VM but no VM was selected")

    def _new_vm(self):
        wizard = CreateVMWizard(app = self.app)
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
            self.manager.delete_vm(name)
            self.vm_list.refresh()

    def _open_config(self):
        settings_dialog = SettingsDialog(self.icon_manager, self.theme_manager)
        if settings_dialog.exec():
            self.vm_list.refresh()
            self._update_buttons()

    def _backend_state_changed(self, name, state):
        self.vm_state_changed.emit(name, state)
        self._update_buttons()


    def _update_vm_ui(self, name, state):
        self.vm_list.update_vm_state(name, state.value)
        print("Triggered list change")

    def _update_vm_files(self):
        main_ver = 2

        logging.debug("Looking for old config files")

        from backend.config_manager import ConfigManager
        config_man = ConfigManager()
        lvms = config_man.list_vms()

        updating = False

        for i in lvms:
            conf = config_man.load_vm(i)
            ver = conf.get("version", 0)
            if ver != main_ver:
                logging.info("Found an outdated VM config file. Updating to a current version")
                
                if not updating:
                    self.udialog = QProgressDialog("Updating VM config files", "Please Wait", 0, 0, self)
                    self.udialog.setWindowModality(Qt.WindowModality.WindowModal)
                    updating = True

                match ver:
                    case 0:
                        logging.info(f"File {i}.json didn't have a version definition. Asuming version 1")
                        config_man.backup_vm(i)
                        try:
                            # video additions
                            old_video_model = conf["video"]
                            conf["video"] = {
                                "model": old_video_model,
                                "connection": "QEMU"
                            }

                            # ids on storage
                            sid = 0
                            for o in conf["storage"]:
                                o["id"] = sid
                                sid += 1
                            
                            # ids on media
                            cid = 0
                            fid = 0
                            for o in conf["media"]:
                                if o["type"] == "CD-ROM":
                                    o["id"] = cid
                                    cid += 1
                                elif o["type"] == "Floppy":
                                    o["id"] = fid
                                    fid += 1
                            conf["version"] = main_ver
                            config_man.save_vm(i, conf)
                        except:
                            logging.warning(f"There was an error while converting {i}.json file. Skipping...")

                    # add more cases when updating
                    case _:
                        logging.info(f"File version of {i}.json isn't valid. Skippping")
        if updating:
            self.udialog.close()

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

    def _manage_double(self):
        name = self.vm_list.get_selected()
        
        if self.vnc_window:
            self.vnc_window.close()
            self.vnc_window = None

        if not self.process.get(name, ""):
            self._start()

        try:
            self.vnc_window = VNCWindow(self.process[name]["config"], self.process[name]["process"], self.app)
            self.vnc_window.destroyed.connect(self._closed_vnc)
            self.vnc_window.show()
        except TypeError:
            logging.warning(f"Tried to open {name} VM's VNC, but is not found...")
    
    def _closed_vnc(self):
        self.vnc_window = None

    def _handle_stop(self, name):
        if self.process.pop(name, False):
            logging.debug(f"Removed VM {name} VNC process")
        else:
            logging.debug(f"Aparently, {name} doesn't exists...")