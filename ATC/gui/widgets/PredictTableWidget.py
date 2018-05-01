import os

import PyQt5.QtWidgets as qw
from pandas import DataFrame
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
        self.is_last_error = False
        # self.option_bar.threshold.valueChanged.connect(self.show_output)
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
        if not self.is_last_error:
            self.output_widget.clear()
        self.is_last_error = True
        self.output_widget.insertHtml("<font color=\"red\">" + error_msg + "</font><br>")

    def show_output(self, output, extension=""):
        self.is_last_error = False
        self.output_widget.clear()
        threshold = self.option_bar.threshold.value()
        self.last_result = output
        self.current_output = ""
        reject = "Не удалось определить рубрики"
        empty = "Нет рубрик с вероятностью больше заданного порога"
        for i in output.index:
            result = output.loc[i, "result"]
            if output.index.name == "id":
                if result is None:
                    str_res = reject
                else:
                    result = result[result > threshold]
                    if len(result.index) == 0:
                        str_res = empty
                    else:
                        str_res = "\\".join(
                                    ["{}-{}".format(j, result.loc[j]) for j in result.index]
                                )
                row = "{}\t{}\n".format(i, str_res)
                self.current_output += row
                self.output_widget.append(row)
            else:
                if result is None:
                    row = reject
                    self.output_widget.append(row)
                else:
                    result = result[result > threshold]
                    if len(result.index) == 0:
                        row = empty
                        self.output_widget.append(row)
                    else:
                        for topic, proba in result.iteritems():
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
