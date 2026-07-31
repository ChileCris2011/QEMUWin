import math

from PyQt6.QtCore import (
    QElapsedTimer,
    QRectF,
    QSize,
    Qt,
    QTimer
)
from PyQt6.QtGui import (
    QColor,
    QFont,
    QFontMetricsF,
    QImage,
    QPainter
)
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout
)


class WaveTextWidget(QWidget):
    def __init__(self, text, parent=None):
        super().__init__(parent)

        self.text = text

        # Wave settings
        self.amplitude = 4.0
        self.wave_spacing = 0.55

        # Wave speed in radians per second.
        # Lower means slower.
        self.wave_speed = 2.5

        # Render at a higher resolution and scale down.
        self.render_scale = 4

        self.text_font = QFont()
        self.text_font.setPointSizeF(11.0)
        self.text_font.setBold(True)

        self.setFixedHeight(45)
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            True
        )

        self.animation_clock = QElapsedTimer()
        self.animation_clock.start()

        self.wave_timer = QTimer(self)
        self.wave_timer.setTimerType(
            Qt.TimerType.PreciseTimer
        )
        self.wave_timer.timeout.connect(
            self.update_animation
        )

        # Approximately 60 FPS :DD
        self.wave_timer.start(16)

    def update_animation(self):
        if self.isVisible():
            self.update()

    def sizeHint(self):
        metrics = QFontMetricsF(self.text_font)

        return QSize(
            math.ceil(
                metrics.horizontalAdvance(self.text)
            ) + 24,
            45
        )

    def minimumSizeHint(self):
        return self.sizeHint()

    def paintEvent(self, event):
        scale = self.render_scale

        image_width = max(1, self.width() * scale)
        image_height = max(1, self.height() * scale)

        image = QImage(
            image_width,
            image_height,
            QImage.Format.Format_ARGB32_Premultiplied
        )
        image.fill(Qt.GlobalColor.transparent)

        image_painter = QPainter(image)

        try:
            image_painter.setRenderHint(
                QPainter.RenderHint.Antialiasing,
                True
            )
            image_painter.setRenderHint(
                QPainter.RenderHint.TextAntialiasing,
                True
            )

            scaled_font = QFont(self.text_font)
            scaled_font.setPointSizeF(
                self.text_font.pointSizeF() * scale
            )

            image_painter.setFont(scaled_font)
            image_painter.setPen(
                QColor(255, 255, 255)
            )

            metrics = QFontMetricsF(scaled_font)

            character_widths = [
                metrics.horizontalAdvance(character)
                for character in self.text
            ]

            total_width = sum(character_widths)

            current_x = (
                image_width - total_width
            ) / 2.0

            baseline_y = (
                image_height
                + metrics.ascent()
                - metrics.descent()
            ) / 2.0

            elapsed_seconds = (
                self.animation_clock.nsecsElapsed()
                / 1_000_000_000.0
            )

            phase = (
                elapsed_seconds * self.wave_speed
            )

            scaled_amplitude = (
                self.amplitude * scale
            )

            for index, character in enumerate(self.text):
                vertical_offset = (
                    scaled_amplitude
                    * math.sin(
                        phase
                        - index * self.wave_spacing
                    )
                )

                character_width = (
                    character_widths[index]
                )

                character_rect = QRectF(
                    current_x,
                    baseline_y
                    - metrics.ascent()
                    + vertical_offset,
                    character_width + scale,
                    metrics.height()
                )

                image_painter.drawText(
                    character_rect,
                    Qt.AlignmentFlag.AlignLeft
                    | Qt.AlignmentFlag.AlignTop,
                    character
                )

                current_x += character_width

        finally:
            if image_painter.isActive():
                image_painter.end()

        painter = QPainter(self)

        try:
            painter.setRenderHint(
                QPainter.RenderHint.SmoothPixmapTransform,
                True
            )

            painter.drawImage(
                self.rect(),
                image
            )

        finally:
            if painter.isActive():
                painter.end()


class AboutPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        layout.addStretch()

        # Program name
        qemuwin_layout = QHBoxLayout()
        qemuwin_layout.addStretch()

        qemuwin = QLabel("QEMUWin")
        qemuwin.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        qemuwin.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
            """
        )

        qemuwin_layout.addWidget(qemuwin)
        qemuwin_layout.addStretch()

        layout.addLayout(qemuwin_layout)

        # Smooth animated author text
        self.author_text = WaveTextWidget(
            "by: ChileCris2011",
            self
        )

        layout.addWidget(
            self.author_text,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        layout.addStretch()
