import json
from PyQt6.QtWidgets import QWizardPage, QVBoxLayout, QTextEdit, QLabel, QLineEdit

class PageSummary(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Summary")

        layout = QVBoxLayout()

        self.summary = QTextEdit()
        self.summary.setReadOnly(True)

        layout.addWidget(self.summary)

        self.args_text = QLabel("Aditional QEMU args (advanced):")
        layout.addWidget(self.args_text)

        self.args_box = QLineEdit()
        layout.addWidget(self.args_box)

        self.setLayout(layout)

    def initializePage(self):
        wizard = self.wizard()
        config = wizard.collect_config()
        self.summary.setText(json.dumps(config, indent=4))

    def get_data(self):
        return {
            "qargs": self.args_box.text().split()
        }