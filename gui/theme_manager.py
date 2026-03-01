from PyQt6.QtCore import Qt, QObject, pyqtSignal, QSettings, QSize
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QGuiApplication, QPalette, QColor, QPixmap, QPainter, QIcon
from PyQt6.QtWidgets import QApplication

import os, resources_rc

class ThemeMode:
    AUTO = "auto"
    LIGHT = "light"
    DARK = "dark"


class ThemeManager(QObject):
    themeChanged = pyqtSignal(str)  # Emite el modo activo real (light/dark)

    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app

        app.setStyle("fusion")

        self.settings = QSettings("QEMUWin", "QEMUWin")

        self._style_hints = QGuiApplication.styleHints()
        self._style_hints.colorSchemeChanged.connect(self._on_system_scheme_changed)

        self._mode = ThemeMode.AUTO

        if self.settings.value("theme/mode"):
            self._mode = self.settings.value("theme/mode")
        else:
            self.settings.setValue("theme/mode", ThemeMode.AUTO)

    # -------------------------
    # API pública
    # -------------------------

    def current_mode(self) -> str:
        return self._mode
    
    def get_mode(self) -> str:
        return self._resolve_effective_mode()

    def set_mode(self, mode: str):
        if mode not in (ThemeMode.AUTO, ThemeMode.LIGHT, ThemeMode.DARK):
            return

        self._mode = mode
        self.settings.setValue("theme/mode", mode)
        self.apply()

    def apply(self):

        effective_mode = self._resolve_effective_mode()

        if effective_mode == ThemeMode.DARK:
            self._apply_dark_palette()
        else:
            self._apply_light_palette()

        self.themeChanged.emit(effective_mode)

    # -------------------------
    # Interno
    # -------------------------

    def _resolve_effective_mode(self) -> str:
        self._mode = self.settings.value("theme/mode")
        if self._mode == ThemeMode.AUTO:
            scheme = self._style_hints.colorScheme()
            if scheme == Qt.ColorScheme.Dark:
                return ThemeMode.DARK
            return ThemeMode.LIGHT
        return self._mode

    def _on_system_scheme_changed(self):
        if self._mode == ThemeMode.AUTO:
            self.apply()

    def _apply_light_palette(self):
        dark_palette = QPalette()

        dark_palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)

        dark_palette.setColor(QPalette.ColorRole.Base, QColor(247, 247, 250))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(247, 245, 245))

        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)

        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)

        dark_palette.setColor(QPalette.ColorRole.Button, QColor(250, 245, 245))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)

        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(210, 210, 210))
        dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(190, 190, 190))

        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215, 127))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)

        self.app.setPalette(dark_palette)

    def _apply_dark_palette(self):
        light_palette = QPalette()

        light_palette.setColor(QPalette.ColorRole.Window, QColor(37, 37, 38))
        light_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)

        light_palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        light_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))

        light_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(42, 42, 42))
        light_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)

        light_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)

        light_palette.setColor(QPalette.ColorRole.Button, QColor(42, 42, 42))
        light_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)

        light_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, QColor(100, 100, 100))
        light_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(190, 190, 190))

        light_palette.setColor(QPalette.ColorRole.Light, QColor(42, 42, 42))
        light_palette.setColor(QPalette.ColorRole.Midlight, QColor(42, 42, 42))
        light_palette.setColor(QPalette.ColorRole.Mid, QColor(42, 42, 42))
        light_palette.setColor(QPalette.ColorRole.Dark, QColor(42, 42, 42))
        light_palette.setColor(QPalette.ColorRole.Shadow, Qt.GlobalColor.black)

        light_palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(42, 42, 42))

        light_palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215, 127))
        light_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)

        light_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)

        self.app.setPalette(light_palette)

class IconManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        # Singleton
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, mode="auto", icon_path="resources/icons", app=QApplication):
        if hasattr(self, "_initialized"):
            return
        
        self.theme_manager = ThemeManager(app)
        self.theme_manager.themeChanged.connect(self._manage_change)

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
        theme = self.theme_manager.get_mode()

        key = (name, size, theme)

        if key in self._cache:
            return self._cache[key]

        icon = self._load_svg_icon(name, size, theme)
        self._cache[key] = icon
        return icon

    # -------------------------
    # Internals
    # -------------------------

    def _icon_color(self):
        mode = self.theme_manager.get_mode()
        if mode == "dark":
            return QColor(230, 230, 230)  # casi blanco
        return QColor(40, 40, 40)  # casi negro

    def _load_svg_icon(self, name: str, size: int, theme: str) -> QIcon:
        return QIcon(f":resources/icons/{theme}/{name}.svg")
    
    # Didn't want to change all. That'll be for v2
    
    def _manage_change(self):
        self.set_mode(self.theme_manager.get_mode())