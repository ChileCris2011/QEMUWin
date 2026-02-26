from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMenu, QMessageBox
from gui.vm_item_widget import VMItemWidget

class VMListWidget(QListWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.setSpacing(8)
        self.refresh()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._open_context_menu)

    def refresh(self):
        self.clear()

        for vm_name in self.manager.list_vms():
            config = self.manager.config.load_vm(vm_name)

            item = QListWidgetItem()
            widget = VMItemWidget(
                vm_name,
                state="stopped",
                memory=config.get("memory", "Unknown")
            )

            item.setSizeHint(widget.sizeHint())

            self.addItem(item)
            self.setItemWidget(item, widget)

    def get_selected(self):
        item = self.currentItem()
        if item:
            widget = self.itemWidget(item)
            return widget.name_label.text()
        return None
    
    def update_vm_state(self, name, state):
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget.name_label.text() == name:
                widget.update_state(state)
                break

    def _open_context_menu(self, position):
        item = self.itemAt(position)
        if not item:
            return

        widget = self.itemWidget(item)
        name = widget.name_label.text()

        menu = QMenu()

        start_action = menu.addAction(f"  Start")
        stop_action = menu.addAction(f"  Stop")
        kill_action = menu.addAction(f"  Quit")
        edit_action = menu.addAction(f"  Edit")
        delete_action = menu.addAction(f"  Delete")

        state = self.manager.get_state(name)

        if state.value == "running":
            start_action.setDisabled(True)
            stop_action.setDisabled(False)
        else:
            stop_action.setDisabled(True)
            start_action.setDisabled(False)

        action = menu.exec(self.mapToGlobal(position))

        if action == start_action:
            self.manager.start_vm(name)

        elif action == stop_action:
            self.manager.stop_vm(name)
        
        elif action == kill_action:
            self.manager.kill_vm(name)

        elif action == edit_action:
            self.parent().parent()._edit_vm()

        elif action == delete_action:
            self.parent().parent()._delete_vm()