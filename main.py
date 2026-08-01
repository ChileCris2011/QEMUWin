import sys, threading, logging
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QIcon
from backend.vm_manager import VMManager
from gui.main_window import MainWindow
from gui.theme_manager import ThemeManager

import backend.error_handling as error_handler

open("./latest.log", "w", encoding="utf-8")

logging.basicConfig(
    filename="latest.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":

    threading.excepthook = error_handler.thread_exception_hook
    sys.excepthook = error_handler.global_exception_hook

    logging.info("----------------------------")
    logging.info("------- QEMUWin Nightly -------")
    logging.info("----------------------------")

    app = QApplication(sys.argv)
    
    app.setWindowIcon(QIcon(":resources/icons/QEMUWin.ico"))

    theme_manager = ThemeManager(app)
    theme_manager.apply()

    manager = VMManager(app)

    window = MainWindow(manager, app)
    window.show()

    logging.debug("Showing window")

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

# TODO: Audio handler (VNC doesn't support audio), finish vncviewer ui (non-working buttons)
