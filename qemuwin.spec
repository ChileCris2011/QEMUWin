from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
import os
from pathlib import Path
import PyQt6

version_snapshot = Path(SPECPATH) / "build" / "version" / "build_version.json"
if not version_snapshot.is_file():
    raise RuntimeError("Missing version metadata. Run python tools/generate_version.py before packaging.")

block_cipher = None

pyqt_path = os.path.dirname(PyQt6.__file__)
qt_path = os.path.join(pyqt_path, "Qt6")

qt_plugins = [
    (
        os.path.join(qt_path, "plugins", "platforms", "qwindows.dll"),
        "PyQt6/Qt6/plugins/platforms"
    )
]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=qt_plugins,
    datas=[(str(version_snapshot), ".")],
    hiddenimports=[
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets"
    ],
    excludes=[
        "PyQt6.QtWebEngineWidgets",
        "PyQt6.QtWebEngineCore",
        "PyQt6.QtWebEngine",
        "PyQt6.QtMultimedia",
        "PyQt6.QtMultimediaWidgets",
        "PyQt6.QtPdf",
        "PyQt6.QtPdfWidgets",
        "PyQt6.QtPositioning",
        "PyQt6.QtBluetooth",
        "PyQt6.QtSensors",
        "PyQt6.QtNfc",
        "PyQt6.QtQuick",
        "PyQt6.QtQml",
        "PyQt6.Qt3DCore",
        "PyQt6.Qt3DRender",
        "PyQt6.QtCharts",
        "PyQt6.QtSql",
        "PyQt6.QtTest",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="QEMUWin",
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon="resources/icons/QEMUWin.ico"
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="QEMUWin",
)
