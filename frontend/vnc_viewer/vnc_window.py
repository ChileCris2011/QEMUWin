from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QApplication,
    QScrollArea, QMenu, QMessageBox,
    QFileDialog
)
from PyQt6.QtGui import QAction, QResizeEvent, QMouseEvent, QShortcut, QKeySequence, QCursor, QKeyEvent

from PyQt6.QtCore import QSize, Qt, QPointF, QEvent
from qvncwidget6 import QVNCWidget

from gui.theme_manager import IconManager

import time

class VNCWindow(QMainWindow):
    def __init__(self, config, process, app=QApplication):
        super().__init__()

        self.setWindowTitle(f"{config["name"]} - VNC Viewer")
        self.resize(800, 600)

        self.app = app

        self.config = config
        self.process = process

        self.paused = False

        self.onPause = None
        self.onChangeMedia = None

        self.oppened = True
        self.resize_to_window = False

        self.start_pos = QCursor.pos()
        self.virtual_pos = QCursor.pos()

        self.ignore_next_event = False

        self.grabbing = False
        self.shortcut = QShortcut(QKeySequence("Ctrl+Alt+G"), self)
        self.shortcut.activated.connect(self._handle_grab)

        self.icons = IconManager(app=self.app)

        central = QWidget()
        main_layout = QVBoxLayout(central)

        self.menu = QHBoxLayout()

        self.btn_pause = QPushButton()
        self.btn_pause.setIcon(self.icons.get_icon("pause"))
        self.btn_pause.setToolTip("Pause VM")
        self.btn_pause.clicked.connect(self._handle_pause)
        self.menu.addWidget(self.btn_pause)

        self.btn_resume = QPushButton()
        self.btn_resume.setIcon(self.icons.get_icon("play_arrow"))
        self.btn_resume.setToolTip("Resume VM")
        self.btn_resume.setEnabled(False)
        self.btn_resume.clicked.connect(self._handle_pause)
        self.menu.addWidget(self.btn_resume)

        self.menu.addSpacing(16)

        media_options = QPushButton("Removable media")
        media_options.setIcon(self.icons.get_icon("disk"))
        media_options.setToolTip("Change removable media")

        self.media_menu = QMenu()
        self.media_menu.aboutToShow.connect(self._refresh_media_menu)
        self._build_media_menu()

        media_options.setMenu(self.media_menu)
        self.menu.addWidget(media_options)

        insert_options = QPushButton("Insert")
        insert_options.setIcon(self.icons.get_icon("insert"))
        insert_options.setToolTip("Insert key combination")

        self.insert_menu = QMenu()
        self._build_insert_menu()

        insert_options.setMenu(self.insert_menu)
        self.menu.addWidget(insert_options)

        self.menu.addStretch()

        size_options = QPushButton()
        size_options.setIcon(self.icons.get_icon("size"))
        size_options.setToolTip("Resize options")

        size_menu = QMenu()

        self.follow_window = QAction("    Resize to Window", self)
        self.follow_window.triggered.connect(self._follow_window)

        size_menu.addAction(self.follow_window)

        size_options.setMenu(size_menu)

        self.menu.addWidget(size_options)

        main_layout.addLayout(self.menu)

        self.viewer_container = QScrollArea()
        self.viewer_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.viewer_container.setContentsMargins(0, 0, 0, 0)

        self.viewer_widget = QWidget()
        self.viewer_widget.setContentsMargins(0, 0, 0, 0)
        self.viewer_widget.mousePressEvent = self._handle_click
        
        self.viewer_layout = QHBoxLayout(self.viewer_widget)
        
        self.viewer = QVNCWidget(
            parent=self.viewer_widget,
            host="127.0.0.1", port=process.vnc_port,
            readOnly=False,
            autoResize= not self.resize_to_window,
            restrict= self.grabbing
        )
        self.viewer.onResize.connect(self._host_resize_event)
        self.viewer.setMouseTracking(False)
        self._viewer_mouse_press_event = self.viewer.mousePressEvent
        self.viewer.mousePressEvent = self._handle_viewer_click

        self.viewer_layout.addWidget(self.viewer)
        self.viewer_layout.setContentsMargins(0, 0, 0, 0)

        self.viewer_container.setWidget(self.viewer_widget)
        self.viewer_container.setWidgetResizable(True)

        main_layout.addWidget(self.viewer_container)

        self.viewer.start()

        self.setCentralWidget(central)

    def _follow_window(self):
        if self.resize_to_window:
            self.resize_to_window = False
            self.viewer.autoResize = True
            self.follow_window.setText("    Resize to window")
            self.viewer.setMinimumSize(self.viewer.sizeHint())
            self.viewer.setFixedSize(self.viewer.sizeHint())
            self.viewer_container.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.viewer_container.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            self.resize_to_window = True
            self.viewer.autoResize = False
            self.follow_window.setText(" ✔  Resize to window")
            self.viewer.setMinimumSize(1, 1)
            self.viewer.setFixedSize(self.viewer_container.size().width() - 8, self.viewer_container.size().height() - 8)
            self.viewer_container.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.viewer_container.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def closeEvent(self, ev):
        try:
            self.oppened = False
            self.close()
            self.viewer.stop()
            return super().closeEvent(ev)
        except OSError:
            pass
    
    def resizeEvent(self, event: QResizeEvent | None):

        if self.resize_to_window:
            self.viewer.setFixedSize(self.viewer_container.size().width() - 8, self.viewer_container.size().height() - 8)
        
        return super().resizeEvent(event)

    def _host_resize_event(self, size: QSize):
        if self.resize_to_window:
            self.viewer.setFixedSize(self.viewer_container.size().width() - 8, self.viewer_container.size().height() - 8)
        else:
            self.viewer.setMinimumSize(size)

    def _handle_click(self, event: QMouseEvent):
        if not self.grabbing:
            self._handle_grab()
            event.accept()

    def _handle_viewer_click(self, event: QMouseEvent):
        if not self.grabbing:
            self._handle_grab()
            event.accept()
            return

        self._viewer_mouse_press_event(event)
    
    def _handle_grab(self):
        if self.grabbing:
            self.viewer.releaseMouse()
            self.viewer.releaseKeyboard()
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.viewer.setMouseTracking(False)
            self.viewer.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.setWindowTitle(f"{self.config["name"]} - VNC Viewer")
            self.grabbing = False
            self.viewer.restricting = False
        else:
            self.viewer.setFocus()
            self.viewer.grabMouse()
            self.viewer.grabKeyboard()
            self.setCursor(Qt.CursorShape.BlankCursor)
            self.start_pos = QCursor.pos()
            self.setWindowTitle(f"{self.config["name"]} - VNC Viewer - Press Ctrl+Alt+G to release grab")
            self.viewer.setMouseTracking(True)
            self.viewer.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.grabbing = True
            self.viewer.restricting = True

    def _handle_pause(self):
        self.paused = not self.paused
        self.btn_pause.setDisabled(self.paused)
        self.btn_resume.setEnabled(self.paused)
        if self.onPause:
            self.onPause(self.config["name"], self.paused)

    def _build_insert_menu(self):
        key_combos = [
            ("    Ctrl+Alt+Del", [Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_Delete]),
            ("    Ctrl+Alt+Backspace", [Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_Backspace]),
            ("    Alt+Tab", [Qt.Key.Key_Alt, Qt.Key.Key_Tab]),
            ("    Alt+F4", [Qt.Key.Key_Alt, Qt.Key.Key_F4]),
            ("    Ctrl+Esc", [Qt.Key.Key_Control, Qt.Key.Key_Escape]),
            ("    Windows key", [Qt.Key.Key_Meta]),
            ("    Print Screen", [Qt.Key.Key_Print]),
            ("    Ctrl+Alt+F1", [Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_F1]),
            ("    Ctrl+Alt+F2", [Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_F2]),
            ("    Ctrl+Alt+F3", [Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_F3]),
        ]

        for label, keys in key_combos:
            action = QAction(label, self)
            action.triggered.connect(lambda checked=False, combo=keys: self._send_key_combo(combo))
            self.insert_menu.addAction(action)

    def _send_key_combo(self, keys):
        self.viewer.setFocus()
        for key in keys:
            self.viewer.keyPressEvent(self._make_key_event(QEvent.Type.KeyPress, key))
        for key in reversed(keys):
            self.viewer.keyReleaseEvent(self._make_key_event(QEvent.Type.KeyRelease, key))

    def _make_key_event(self, event_type, key):
        return QKeyEvent(event_type, key, Qt.KeyboardModifier.NoModifier, "")

    def _refresh_media_menu(self):
        self.media_menu.clear()
        self._build_media_menu()

    def _build_media_menu(self):
        media_items = self._get_media_items()

        if not media_items:
            empty_action = QAction("    No removable media", self)
            empty_action.setEnabled(False)
            self.media_menu.addAction(empty_action)
            return

        cdroms = [item for item in media_items if item.get("type") == "CD-ROM"]
        floppies = [item for item in media_items if item.get("type") == "Floppy"]

        self._add_media_category(self.media_menu, "CD-ROM", cdroms)
        self._add_media_category(self.media_menu, "Floppy", floppies)

    def _add_media_category(self, root_menu, title, media_items):
        category_menu = root_menu.addMenu(f"    {title}")

        if not media_items:
            empty_action = QAction("    No drives", self)
            empty_action.setEnabled(False)
            category_menu.addAction(empty_action)
            return

        for media in media_items:
            media_id = media.get("id", 0)
            media_path = media.get("path", "Empty")
            drive_menu = category_menu.addMenu(f"    {title} {media_id}: {self._media_filename(media_path)}")

            choose_action = QAction("    Choose disk image...", self)
            choose_action.triggered.connect(lambda checked=False, item=media: self._select_media_file(item))
            drive_menu.addAction(choose_action)

            eject_action = QAction("    Eject", self)
            eject_action.triggered.connect(lambda checked=False, item=media: self._eject_media(item))
            drive_menu.addAction(eject_action)

    def _get_media_items(self):
        media = self.config.get("media", [])

        if isinstance(media, dict):
            media = media.values()

        return [
            item for item in media
            if item.get("type") in ("CD-ROM", "Floppy")
        ]

    def _media_filename(self, path):
        if path in ("Empty", "", " ", "empty", None):
            return "Empty"

        return str(path).replace("\\", "/").split("/")[-1]

    def _select_media_file(self, media):
        if media.get("type") == "CD-ROM":
            title = "Select CD-ROM Image"
            file_filter = "CD-ROM Images (*.iso);;Disk Images (*.iso *.img *.raw);;All Files (*)"
        else:
            title = "Select Floppy Image"
            file_filter = "Floppy Images (*.img *.ima *.flp);;Disk Images (*.img *.ima *.flp *.raw);;All Files (*)"

        path, _ = QFileDialog.getOpenFileName(self, title, filter=file_filter)
        if path:
            self._handle_media_change(media, path)

    def _eject_media(self, media):
        self._handle_media_change(media, "Empty")

    def _handle_media_change(self, media, path):
        updated_media = dict(media)
        updated_media["path"] = path

        try:
            if self.onChangeMedia:
                self.onChangeMedia(self.config["name"], updated_media)
            elif hasattr(self, "process") and self.process:
                self.process.change_media(updated_media)

            media["path"] = path
        except Exception as e:
            QMessageBox.critical(
                self,
                "Media Change Failed",
                f"Could not change {updated_media.get('type')} {updated_media.get('id')}.\n\n{e}"
            )
    
    def _state_changed(self, name, state):
        if name == self.config["name"]:
            if (state.value == "paused" and not self.paused) or (state.value == "running" and self.paused):
                print("External change (pause/resume)")
                self._handle_pause()
            
            elif state.value == "stopped" or state.value == "killed" or state.value == "error":
                print("Closing VNC window")
                self.close()

    def _handle_flop(self):
        pass

    def _handle_disk(self):
        pass


    def mouseMoveEvent(self, a0):
        return super().mouseMoveEvent(a0)

    def mousePressEvent(self, a0):
        if self.grabbing:
            self.viewer.mousePressEvent(a0)
        return super().mousePressEvent(a0)
    
    def mouseReleaseEvent(self, a0):
        if self.grabbing:
            self.viewer.mouseReleaseEvent(a0)
        return super().mouseReleaseEvent(a0)
    
    def keyPressEvent(self, a0):
        if self.grabbing:
            self.viewer.keyPressEvent(a0)
        return super().keyPressEvent(a0)
    
    def keyReleaseEvent(self, a0):
        if self.grabbing:
            self.viewer.keyReleaseEvent(a0)
        return super().keyReleaseEvent(a0)
