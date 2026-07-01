from PyQt6.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QPushButton, QApplication,
    QScrollArea, QMenu
)
from PyQt6.QtGui import QAction, QResizeEvent, QMouseEvent, QShortcut, QKeySequence, QCursor

from PyQt6.QtCore import QSize, Qt, QPointF, QEvent
from qvncwidget6 import QVNCWidget

from gui.theme_manager import IconManager

class VNCWindow(QMainWindow):
    def __init__(self, config, process, app=QApplication):
        super().__init__()

        self.setWindowTitle(f"{config["name"]} - VNC Viewer")
        self.resize(800, 600)

        self.app = app

        self.config = config

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

        btn_pause = QPushButton()
        btn_pause.setIcon(self.icons.get_icon("pause"))
        btn_pause.setToolTip("Pause VM")
        self.menu.addWidget(btn_pause)

        btn_resume = QPushButton()
        btn_resume.setIcon(self.icons.get_icon("play_arrow"))
        btn_resume.setToolTip("Resume VM")
        btn_resume.setEnabled(False)
        self.menu.addWidget(btn_resume)

        self.menu.addSpacing(16)

        # Get all media to assign buttons

        self.disk_btn = {}
        self.floppy_btn = {}
        
        if config.get("media"):
            print(config.get("media"))
            for media in config.get("media"):
                print(media["type"])

                if media["type"] == "CD-ROM":
                    disk_num = media["id"]
                    self.disk_btn[disk_num] = QPushButton()
                    if disk_num < 9:
                        self.disk_btn[disk_num].setIcon(self.icons.get_icon(f"disk_{disk_num}"))
                    else:
                        self.disk_btn[disk_num].setIcon(self.icons.get_icon("disk_plus"))
                    self.disk_btn[disk_num].setToolTip(f"CD-ROM {disk_num}")
                    self.menu.addWidget(self.disk_btn[disk_num])

                elif media["type"] == "Floppy":
                    flop_num = media["id"]
                    self.floppy_btn[flop_num] = QPushButton()
                    self.floppy_btn[flop_num].setIcon(self.icons.get_icon(f"floppy_{flop_num}")) # QEMU doesn't accepts more than 2 floppy drives, so no need to verify
                    self.floppy_btn[flop_num].setToolTip(f"Floppy {flop_num}")
                    self.menu.addWidget(self.floppy_btn[flop_num])

        print(self.disk_btn)
        print(self.floppy_btn)

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
            host="127.0.0.1", port=config["video"]["port"],
            readOnly=False,
            autoResize= not self.resize_to_window
        )
        self.viewer.onResize.connect(self._host_resize_event)
        self.viewer.setMouseTracking(False)

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
        if event.button() == Qt.MouseButton.LeftButton and not self.grabbing:
            self._handle_grab()
    
    def _handle_grab(self):
        if self.grabbing:
            self.viewer.releaseMouse()
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.viewer.setMouseTracking(False)
            self.viewer.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.setWindowTitle(f"{self.config["name"]} - VNC Viewer")
            self.grabbing = False
        else:
            self.viewer.setFocus()
            self.viewer.grabMouse()
            self.setCursor(Qt.CursorShape.BlankCursor)
            self.start_pos = QCursor.pos()
            self.setWindowTitle(f"{self.config["name"]} - VNC Viewer - Press Ctrl+Alt+G to release grab")
            self.viewer.setMouseTracking(True)
            self.viewer.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.grabbing = True

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