import traceback, faulthandler, logging
from gui.error_dialog import ErrorDialog
from PyQt6.QtCore import QTimer

log_file = open("latest.log", "a", encoding="utf-8")
faulthandler.enable(log_file)

def exception_hook(exc_type, exc_value, trace):
    error_text = ''.join(
        traceback.format_exception(exc_type, exc_value, trace)
    )
    logging.exception(f"[Python Exception] {error_text}")
    show_error_dialog(str(exc_value), error_text)

def thread_exception_hook(args):
    error_text = ''.join(
        traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)
    )
    logging.exception(f"[Thread Exception] {error_text}")
    show_error_dialog(str(args.exc_value), error_text)

def global_exception_hook(exctype, value, tb):
    error_text = ''.join(
        traceback.format_exception(exctype, value, tb)
    )
    logging.exception(f"[Global Exception] {error_text}")
    show_error_dialog(str(value), error_text)

def show_error_dialog(message, details):
    QTimer.singleShot(0, lambda: _show_error_dialog(message, details))

def _show_error_dialog(message, details):
    dialog = ErrorDialog(message, details)
    dialog.exec()