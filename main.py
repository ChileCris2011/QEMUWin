import sys
import threading
import time
from PyQt6.QtWidgets import QApplication
from backend.vm_manager import VMManager
from gui.main_window import MainWindow
from gui.theme_manager import ThemeManager

import backend.error_handling as error_handler

import logging

logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def rebuild_ui():
    window._build_ui()

if __name__ == "__main__":

    threading.excepthook = error_handler.thread_exception_hook
    sys.excepthook = error_handler.global_exception_hook
    logging.info("----------------------------")
    logging.info("----QEMUWin V1.2-nightly----")
    logging.info("----------------------------")

    app = QApplication(sys.argv)

    theme_manager = ThemeManager(app)
    theme_manager.apply()
    theme_manager.themeChanged.connect(rebuild_ui)

    manager = VMManager()

    window = MainWindow(manager, app)
    window.show()

    sys.exit(app.exec())

# TODO: Pantalla embebida, apartado de configuración con QEMU path y ubicación de configuraciones, auto-detectar QEMU, warning window for no vm name