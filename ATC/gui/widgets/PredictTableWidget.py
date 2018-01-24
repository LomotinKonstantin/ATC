from PyQt5 import QtWidgets as qw

from common.predict import Predict


###
### TODO: implement PredictTableWidget inherited from QTableView
###


class PredictTableWidget(qw.QTableWidget):
    def __init__(self, descriptions, parent=None):
        super().__init__(parent)
        self.displayed_predict = None
        self.descriptions = descriptions
        self.setEditTriggers(qw.QAbstractItemView.NoEditTriggers)

    def displayResult(self, predict: Predict):
        self.displayed_predict = predict
        result = predict.data.loc[0, "result"]
        print(result)
        if predict.getFormat() != "multidoc":
            self.setRowCount(len(result.index))
            self.setColumnCount(2)
            self.setHorizontalHeaderLabels(["Рубрика", "Вероятность"])
            for ni, i in enumerate(result.index):
                topic_cell = qw.QTableWidgetItem(i)
                self.setItem(ni, 0, topic_cell)
                proba_cell = qw.QTableWidgetItem(str(result[i]))
                self.setItem(ni, 1, proba_cell)
        self.showDescriptions()

    def showDescriptions(self):
        if self.displayed_predict.getFormat() == "multidoc":
            return


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    from pandas import DataFrame, Series

    test_df = DataFrame({"text": ["hohoho, hahaha"],
                         "vector": [[1, 2, 3]],
                         "result": [Series([0.1, 0.3, 0.6, 0.234],
                                           ["e8", "e7", "f1", "wtf"])]})
    # print(test_df.columns)
    # for i in test_df.index:
    #     s = ""
    #     for j in test_df.columns:
    #         s += "{} ".format(test_df.loc[i, j])
    #     print(s)
    # print(test_df)
    test_predict = Predict(test_df, "ru", "plain", "SUBJ", "1.5")
    a = QApplication(sys.argv)
    m = PredictTableWidget("")
    m.displayResult(test_predict)
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
