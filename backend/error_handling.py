import traceback, faulthandler
from gui.error_dialog import ErrorDialog

log_file = open("app.log", "a", encoding="utf-8")
faulthandler.enable(log_file)

def thread_exception_hook(args):
    error_text = ''.join(
        traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)
    )
    show_error_dialog(str(args.exc_value), error_text)

def global_exception_hook(exctype, value, tb):
    error_text = ''.join(traceback.format_exception(exctype, value, tb))
    show_error_dialog(str(value), error_text)

def show_error_dialog(message, details):
    dialog = ErrorDialog(message, details)
    dialog.exec()