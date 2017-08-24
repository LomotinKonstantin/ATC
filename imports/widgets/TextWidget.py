import PyQt5.QtWidgets as qw
from pandas import Series


class TextWidget(qw.QWidget):

    def __init__(self, option_bar, parent=None):
        super().__init__(parent)
        layout = qw.QVBoxLayout()
        self.option_bar = option_bar
        self.current_output = None
        self.option_bar.threshold.valueChanged.connect(self.show_output)
        self.setLayout(layout)
        # Input widget
        self.input_widget = qw.QTextEdit()
        layout.addWidget(self.input_widget)
        # Output widget
        self.output_widget = qw.QTextEdit()
        self.output_widget.setReadOnly(True)
        self.output_widget.setPlaceholderText("Здесь будет результат!")
        layout.addWidget(self.output_widget)

    def indicate_error(self, error_msg="Error!"):
        self.output_widget.insertHtml("<font color=\"red\">" + error_msg + "</font><br>")

    def show_output(self, output):
        self.output_widget.clear()
        threshold = self.option_bar.options_to_dict()["threshold"]
        if isinstance(output, Series):
            self.current_output = output
        if isinstance(self.current_output, Series):
            for topic, proba in self.current_output[self.current_output > threshold].iteritems():
                self.output_widget.append("{}\t{}".format(topic, proba))
        self.output_widget.verticalScrollBar().setValue(0)

    def show_text(self, text):
        self.output_widget.setText("")
        self.input_widget.setText(text)

    def get_input(self):
        return self.input_widget.toPlainText()

    def get_output(self):
        return self.output_widget.toPlainText()