from PyQt5 import QtWidgets as qw

from common.predict import Predict


###
### TODO: implement PredictTableWidget inherited from QTableView
###
from PyQt5.QtGui import QKeyEvent


class PredictTableWidget(qw.QTableWidget):
    def __init__(self, descriptions, parent=None):
        """
        This class can display multidoc, plain and divided results in table,
        apply threshold and show topics descriptions
        :param descriptions: a dict of
                {
                    "RUBR_ID1": {
                                "topic11": "desc11",
                                ...
                                "topic1N": "desc1N"
                                }
                    ...
                    "RUBR_IDM": {
                                "topicM1": "descM1",
                                ...
                                "topicMK": "descMK"
                                }
                }
        :param parent: QObject parent
        """
        super().__init__(parent)
        self.last_predict = None
        self.descriptions = descriptions
        self.threshold = 0.0
        self.descriptions_on = False
        self.setEditTriggers(qw.QAbstractItemView.NoEditTriggers)

    def displayResult(self, predict: Predict):
        print()
        self.last_predict = predict
        if predict.getFormat() == "multidoc":
            row_num = 0
            df = predict.data
            model = {}
            for i in predict.data.index:
                res = df.loc[i, "result"]
                res = res[res > self.threshold]
                row_num += len(res.index)
                model[i] = res
            col_num = 4 if self.descriptions_on else 3
            self.setRowCount(row_num)
            self.setColumnCount(col_num)
            labels = ["ID текста", "Рубрика", "Вероятность"]
            if self.descriptions_on:
                labels.append("Расшифровка")
            self.setHorizontalHeaderLabels(labels)
            actual_row = 0
            for i, index in enumerate(model):
                print(actual_row)
                res = model[index]
                index_cell = qw.QTableWidgetItem(index)
                self.setItem(actual_row, 0, index_cell)
                span = len(res.index)
                self.setSpan(actual_row, 0, span, 1)
                for j, topic in enumerate(res.index):
                    next_row = j + actual_row
                    topic_cell = qw.QTableWidgetItem(topic)
                    self.setItem(next_row, 1, topic_cell)
                    proba_cell = qw.QTableWidgetItem(str(res[topic]))
                    self.setItem(next_row, 2, proba_cell)
                    if self.descriptions_on:
                        description = self.descriptions[predict.getRubrId()]
                        desc_cell = qw.QTableWidgetItem(description[topic])
                        self.setItem(next_row, 3, desc_cell)
                actual_row += span
        else:
            result = predict.data.loc[0, "result"]
            row_num = len(result.index)
            col_num = 3 if self.descriptions_on else 2
            self.setRowCount(row_num)
            self.setColumnCount(col_num)
            labels = ["Рубрика", "Вероятность"]
            if self.descriptions_on:
                labels.append("Расшифровка")
            self.setHorizontalHeaderLabels(labels)
            for ni, i in enumerate(result.index):
                topic_cell = qw.QTableWidgetItem(i)
                self.setItem(ni, 0, topic_cell)
                proba_cell = qw.QTableWidgetItem(str(result[i]))
                self.setItem(ni, 1, proba_cell)
                if self.descriptions_on:
                    description = self.descriptions[predict.getRubrId()]
                    desc_cell = qw.QTableWidgetItem(description[i])
                    self.setItem(ni, 2, desc_cell)

    def onDescriptionsSwitchTurned(self, state):
        self.descriptions_on = state == 2
        self.updateTable()

    def onThresholdChanged(self, new_threshold: float):
        self.threshold = new_threshold
        self.updateTable()

    def updateTable(self):
        self.displayResult(self.last_predict)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == qt.Key_Left:
            self.descriptions_on = False
        elif event.key() == qt.Key_Right:
            self.descriptions_on = True
        elif event.key() == qt.Key_Up:
            self.threshold = min([10, self.threshold + 0.1])
        elif event.key() == qt.Key_Down:
            self.threshold = max([0, self.threshold - 0.1])
        self.setWindowTitle(str(self.threshold))
        self.updateTable()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    from PyQt5.Qt import Qt as qt
    import sys
    from pandas import DataFrame, Series

    descriptions = {
        "IPV": {
            "de": "das ist Deutsch",
            "en": "this is English",
            "ru": "это русский"
        },
        "SUBJ": {
            "e8": "math",
            "e7": "biology",
            "f1": "electronics",
            "wtf": "SoC"
        }
    }

    index = ["abc1", "soc2", "ooo20"]
    entry = {"text": ["hohoho, hahaha", "wololo", "look at my horse"],
             "vector": [[1, 2, 3], [0.2, 0.1, 0], [5, 5, 5]],
             "result": [Series([0.1, 0.3, 0.6, 0.234],
                               ["e8", "e7", "f1", "wtf"]),
                        Series([1, 2, 3, 4],
                               ["e8", "e7", "f1", "wtf"]),
                        Series([0.01, 0.02, 5, 10],
                               ["e8", "e7", "f1", "wtf"])
                        ]}

    test_df = DataFrame(entry, index=index)

    # print(test_df.columns)
    # for i in test_df.index:
    #     s = ""
    #     for j in test_df.columns:
    #         s += "{} ".format(test_df.loc[i, j])
    #     print(s)
    # print(test_df)
    test_predict = Predict(test_df, "ru", "multidoc", "SUBJ", "1.5")
    a = QApplication(sys.argv)
    m = PredictTableWidget(descriptions)
    m.displayResult(test_predict)
    m.onDescriptionsSwitchTurned(2)
    m.show()
    a.exec()


class TextWidget(qw.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = qw.QVBoxLayout()
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
        path_to_res = os.path.join(os.path.dirname(__file__), "..", "..", "resources")
        subj_path = os.path.join(path_to_res, "SUBJ.txt")
        self.subj_df = pd.read_csv(subj_path,
                                   encoding="cp1251", sep="\t", index_col=0, names=["description"])
        ipv_path = os.path.join(path_to_res, "IPV.txt")
        self.ipv_df = pd.read_csv(ipv_path,
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
