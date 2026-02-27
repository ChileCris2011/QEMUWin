from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QApplication
import os


class IconManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        # Singleton
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, mode="auto", icon_path="resources/icons"):
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self.mode = mode  # auto | light | dark
        self.icon_path = icon_path
        self._cache = {}

    # -------------------------
    # Public API
    # -------------------------

    def set_mode(self, mode: str):
        """
        Cambia el modo y limpia caché.
        mode: auto | light | dark
        """
        self.mode = mode
        self._cache.clear()

    def get_icon(self, name: str, size: int = 40) -> QIcon:
        """
        Obtiene un QIcon recoloreado dinámicamente.
        """
        key = (name, size, self._effective_mode())

        if key in self._cache:
            return self._cache[key]

        icon = self._load_svg_icon(name, size)
        self._cache[key] = icon
        return icon

    # -------------------------
    # Internals
    # -------------------------

    def _effective_mode(self):
        if self.mode == "auto":
            return self._detect_system_theme()
        return self.mode

    def _detect_system_theme(self):
        # Método simple y bastante fiable
        palette = QApplication.palette()
        base_color = palette.color(palette.ColorRole.Window)

        # Si el fondo es oscuro → dark
        brightness = (
            base_color.red() * 0.299 +
            base_color.green() * 0.587 +
            base_color.blue() * 0.114
        )

        return "dark" if brightness < 128 else "light"

    def _icon_color(self):
        mode = self._effective_mode()
        if mode == "dark":
            return QColor(230, 230, 230)  # casi blanco
        return QColor(40, 40, 40)  # casi negro

    def _load_svg_icon(self, name: str, size: int) -> QIcon:
        file_path = os.path.join(self.icon_path, f"{name}.svg")

        if not os.path.exists(file_path):
            return QIcon()

        renderer = QSvgRenderer(file_path)

        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), self._icon_color())
        painter.end()

        return QIcon(pixmap)