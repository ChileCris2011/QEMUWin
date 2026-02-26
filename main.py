import sys
import threading
from PySide6.QtWidgets import QApplication
from backend.vm_manager import VMManager
from gui.main_window import MainWindow

import backend.error_handling as error_handler

import logging

logging.basicConfig(
    filename="app.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    manager = VMManager()
    window = MainWindow(manager)
    window.show()

    threading.excepthook = error_handler.thread_exception_hook
    sys.excepthook = error_handler.global_exception_hook

    sys.exit(app.exec())