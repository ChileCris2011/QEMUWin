import json
from PyQt6.QtWidgets import QWizardPage, QVBoxLayout, QTextEdit

class PageSummary(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Summary")

        layout = QVBoxLayout()

        self.summary = QTextEdit()
        self.summary.setReadOnly(True)

        layout.addWidget(self.summary)
        self.setLayout(layout)

    def initializePage(self):
        wizard = self.wizard()
        config = wizard.collect_config()
        self.summary.setText(json.dumps(config, indent=4))