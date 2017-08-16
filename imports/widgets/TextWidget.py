import PyQt5.QtWidgets as qw


class TextWidget(qw.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = qw.QVBoxLayout()
        self.setLayout(layout)
        # Input widget
        self.input_widget = qw.QTextEdit()
        layout.addWidget(self.input_widget)
        # Output widget
        self.output_widget = qw.QTextEdit()
        self.output_widget.setReadOnly(True)
        self.output_widget.setPlaceholderText("Здесь будет результат!")
        layout.addWidget(self.output_widget)