import sys, threading, logging
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QSettings
from backend.vm_manager import VMManager
from gui.main_window import MainWindow
from gui.theme_manager import ThemeManager

import backend.error_handling as error_handler

open("./latest.log", "w", encoding="utf-8")

logging.basicConfig(
    filename="latest.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def rebuild_ui():
    window._build_ui()

if __name__ == "__main__":

    threading.excepthook = error_handler.thread_exception_hook
    sys.excepthook = error_handler.global_exception_hook
    logging.info("----------------------------")
    logging.info("-------- QEMUWin V1 --------")
    logging.info("----------------------------")

    app = QApplication(sys.argv)

    theme_manager = ThemeManager(app)
    theme_manager.apply()
    theme_manager.themeChanged.connect(rebuild_ui)

    manager = VMManager()

    window = MainWindow(manager, app)
    window.show()

    settings = QSettings("QEMUWin", "QEMUWin")
    if settings.value("QEMUWin", 0) == 0:
        message = QMessageBox.question(
            None,
            "QEMUWin",
            f"This is your first time running QEMUWin.\n\nDo you want to set the QEMU path?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if message == QMessageBox.StandardButton.Yes:
            window._open_config()

        settings.setValue("QEMUWin", 1)

    sys.exit(app.exec())

# TODO: Pantalla embebida