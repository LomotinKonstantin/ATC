import os

import PyQt5.QtWidgets as qw
from pandas import DataFrame
import pandas as pd

from common.predict import Predict


class ResultWidget(qw.QTextEdit):
    def __init__(self, parent=None):
        super(ResultWidget, self).__init__(parent)
        self.current_output = None
        self.last_result = None
        # self.option_bar.threshold.valueChanged.connect(self.show_output)
        # Input widget
        # Output widget
        self.output_widget = qw.QTextEdit()
        self.setReadOnly(True)
        self.setPlaceholderText("Здесь будет результат!")
        # Loading descriptions
        self.subj_df = self.loadTopicStrings("SUBJ.txt")
        self.ipv_df = self.loadTopicStrings("IPV.txt")
        self.extended_str = "{}\t<font color='#6c6874'>{}</font><br><br>"

    def show_output(self, output: Predict, params: dict):
        """
        Display the result of analysis
        :param output: DataFrame containing the result
        :param params: Dict with options
        :return: None
        """
        self.clear()
        threshold = params["threshold"]
        if params["topic_names_allowed"]:
            extension = output.getRubrId()
        else:
            extension = ""
        data = output.getPredict()
        self.last_result = output
        self.current_output = ""
        reject = "Не удалось определить рубрики"
        empty = "Нет рубрик с вероятностью больше заданного порога"
        for i in data.index:
            result = data.loc[i, "result"]
            if data.index.name == "id":
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
                self.append(row)
            else:
                if result is None:
                    row = reject
                    self.append(row)
                else:
                    result = result[result > threshold]
                    if len(result.index) == 0:
                        row = empty
                        self.append(row)
                    else:
                        for topic, proba in result.iteritems():
                            row = "{}\t{}\n".format(topic, proba)
                            self.current_output += row
                            if extension == "SUBJ":
                                self.insertHtml(
                                    self.extended_str.format(row, self.subj_df.loc[topic, "description"]))
                            elif extension == "IPV":
                                self.insertHtml(
                                    self.extended_str.format(row, self.ipv_df.loc[topic, "description"]))
                            else:
                                self.append(row)
        self.verticalScrollBar().setValue(0)

    def show_text(self, text):
        self.setText("")
        self.last_result = None
        self.input_widget.setText(text)

    def get_output(self):
        return self.last_result

    def loadTopicStrings(self, filename: str) -> DataFrame:
        file_path = os.path.join(os.path.dirname(__file__),
                                 "..",
                                 "..",
                                 "resources",
                                 filename)
        return pd.read_csv(file_path,
                           encoding="cp1251",
                           sep="\t",
                           index_col=0,
                           names=["description"])

    def update_output(self, params: dict):
        if self.last_result is None:
            return
        self.show_output(self.last_result, params)

