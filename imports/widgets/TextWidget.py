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

    def indicate_error(self, error_msg="Error!"):
        self.output_widget.insertHtml("<font color=\"red\">" + error_msg + "</font><br>")


    def show_output(self, output):
        if isinstance(output, dict):
            self.output_widget.setText("")
            for i, j in output.items():
                self.output_widget.append(str(i) + "\t" + str(j) + "\n")
        else:
            self.output_widget.setText(output)

    def show_text(self, text):
        self.output_widget.setText("")
        self.input_widget.setText(text)

    def get_input(self):
        return self.input_widget.toPlainText()

    def get_output(self):
        return self.output_widget.toPlainText()