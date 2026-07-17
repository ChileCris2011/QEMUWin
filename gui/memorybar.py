import ctypes

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, QSpinBox
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]

def _get_ram():
    mem = MEMORYSTATUSEX()
    mem.dwLength = ctypes.sizeof(mem)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem))

    return {
        "total": int(mem.ullTotalPhys/(1024**2)),
        "avail": int(mem.ullAvailPhys/(1024**2))
    }

class PaintBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(8)

    def paintEvent(self, a0):
        p = QPainter(self)

        w = self.width()

        h = 8

        self.listram = _get_ram()

        avail_per = self.listram["avail"] / self.listram["total"]

        green = int(w * avail_per)
        yellow = int(w * (1 - avail_per - 0.25))
        orange = int(w * 0.20)

        p.fillRect(0, 0, green, h, QColor("#4CAF50"))
        p.fillRect(green, 0, yellow, h, QColor("#FFC107"))
        p.fillRect(green + yellow, 0, orange, h, QColor("#DD6D12"))
        p.fillRect(green + yellow + orange, 0, w, h, QColor("#E61818"))

        p.end()
    
class MemoryBar(QWidget):
    def __init__(self):
        super().__init__()

        ilayout = QVBoxLayout()

        self.listram = _get_ram()

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(self.listram["total"])

        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(128)

        ilayout.addWidget(self.slider)

        color_bar = PaintBar()
        ilayout.addWidget(color_bar)

        ilayout.setSpacing(0)

        tlayout = QVBoxLayout()
        tlayout.addSpacing(4)
        tlayout.addWidget(QLabel(f"Total system RAM: {self.listram["total"]} MiB"))
        tlayout.addWidget(QLabel(f"Available RAM: {self.listram["avail"]} MiB"))

        tlayout.addSpacing(8)

        self.warn_label = QLabel("")
        self.warn_label.setWordWrap(True)
        self.warn_label.setStyleSheet("color: #B86A00;")
        tlayout.addWidget(self.warn_label)

        tlayout.setSpacing(2)

        ilayout.addLayout(tlayout)

        layout = QHBoxLayout()
        layout.addLayout(ilayout)

        self.side_ram = QSpinBox()
        self.side_ram.setMinimum(1)
        self.side_ram.setMaximum(self.listram["total"])
        self.side_ram.setMinimumWidth(100)

        self.slider.sliderMoved.connect(self._handle_change_slide)
        self.slider.sliderReleased.connect(self._handle_change_slide)
        self.side_ram.valueChanged.connect(self._handle_change_spin)

        layout.addWidget(self.side_ram)

        self.setLayout(layout)

    def setValue(self, value: int):
        self.slider.setValue(value)
        self.side_ram.setValue(value)
    
    def _handle_change_slide(self):
        self.side_ram.setValue(self.slider.value())
        self._handle_change()
    def _handle_change_spin(self):
        self.slider.setValue(self.side_ram.value())
        self._handle_change()

    def _handle_change(self):
        total_ram = self.listram["total"]
        avail_ram = self.listram["avail"]
        if self.slider.value() >= (total_ram * 0.95):
            self.warn_label.setText("You shouldn't assign all system RAM")
        elif self.slider.value() >= (total_ram  * 0.75):
            self.warn_label.setText("Guest may not start or system may crash. Assign less RAM to prevent this")
        elif self.slider.value() >= (avail_ram):
            self.warn_label.setText("System available RAM is less than the assigned RAM. System may run out of RAM quickly")
        else:
            self.warn_label.setText("")
    def get_ram(self):
        return _get_ram()