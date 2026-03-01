from PyQt6.QtWidgets import (
    QWidget, QFormLayout,
    QLineEdit, QLabel
)


class ArgsPage(QWidget):
    def __init__(self, config):
        super().__init__()

        args = " ".join(config.get("qargs"))

        print(f"Args received: {args}\n\n")

        layout = QFormLayout()

        self.title = QLabel("Aditional QEMU args (advanced):")

        self.args_text = QLineEdit(args)

        layout.addRow(self.title)
        layout.addRow(self.args_text)

        self.setLayout(layout)

    def get_data(self) -> list[str]:
        return {"args": self.args_text.text().split()}