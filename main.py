import sys
from PySide6.QtWidgets import QApplication
from backend.vm_manager import VMManager
from gui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    manager = VMManager()
    window = MainWindow(manager)
    window.show()

    sys.exit(app.exec())

#TODO: Manage errors visually, add kill button