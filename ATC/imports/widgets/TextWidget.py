import os

import PyQt5.QtWidgets as qw
from pandas import Series
import pandas as pd


class PlainTextWidget(qw.QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def insertFromMimeData(self, md):
        if not (md.hasText() or md.hasHtml()):
            return
        self.insertPlainText(md.text())


class TextWidget(qw.QWidget):
    def __init__(self, option_bar, parent=None):
        super().__init__(parent)
        layout = qw.QVBoxLayout()
        self.option_bar = option_bar
        self.current_output = None
        self.last_result = None
        self.option_bar.threshold.valueChanged.connect(self.show_output)
        self.setLayout(layout)
        # Input widget
        self.input_widget = PlainTextWidget()
        layout.addWidget(self.input_widget)
        # Output widget
        self.output_widget = qw.QTextEdit()
        self.output_widget.setReadOnly(True)
        self.output_widget.setPlaceholderText("Здесь будет результат!")
        layout.addWidget(self.output_widget)
        # Loading descriptions
        self.subj_df = pd.read_csv(os.path.dirname(__file__) + "/SUBJ.txt",
                                   encoding="cp1251", sep="\t", index_col=0, names=["description"])
        self.ipv_df = pd.read_csv(os.path.dirname(__file__) + "/IPV.txt",
                                  encoding="cp1251", sep="\t", index_col=0, names=["description"])
        self.extended_str = "{}\t<font color='#6c6874'>{}</font><br><br>"

    def indicate_error(self, error_msg="Error!"):
        self.output_widget.insertHtml("<font color=\"red\">" + error_msg + "</font><br>")

    def show_output(self, output, extension=""):
        self.output_widget.clear()
        threshold = self.option_bar.threshold.value()
        if isinstance(output, Series):
            self.last_result = output
            self.current_output = ""
            for topic, proba in output[output > threshold].iteritems():
                row = "{}\t{}\n".format(topic, proba)
                self.current_output += row
                if extension == "SUBJ":
                    self.output_widget.insertHtml(
                        self.extended_str.format(row, self.subj_df.loc[topic, "description"]))
                elif extension == "IPV":
                    self.output_widget.insertHtml(
                        self.extended_str.format(row, self.ipv_df.loc[topic, "description"]))
                else:
                    self.output_widget.append(row)
        self.output_widget.verticalScrollBar().setValue(0)

    def show_text(self, text):
        self.output_widget.setText("")
        self.last_result = None
        self.input_widget.setText(text)

    def get_input(self):
        return self.input_widget.toPlainText()

    def get_output(self):
        return self.last_result
