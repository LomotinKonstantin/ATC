import os
from pandas import Series
###
### TODO: implement Predict class to store the result of classification
###


class Predict:
    """
    The class for storing classification result. Provides
    methods for different representations of the result.
    """

    def __init__(self, predict=None, lang=None, text_format=None, rubr_id=None, version=None):
        self.data = None
        self.params = {
            "language": None,
            "format": None,
            "rubr_id": None,
            "version": None
        }
        self.setPredict(predict, lang, text_format, rubr_id, version)
        return

    def saveToFile(self, file, threshold=0, n_digits=3):
        """
        Saves the predict to the provided file
        :param threshold: probability threshold. All answers with lower proba will be rejected
        :param file: either a open file or a filename
        :param n_digits: number of digits after the decimal point
        :return: None
        """
        close_file = False
        if isinstance(file, str):
            dest_file = open(file, "w", encoding="cp1251")
            close_file = True
        else:
            dest_file = file
        data_to_save = self.data.round(n_digits)
        if dest_file.read() == "":
            dest_file.write("#\t{}\t{}\t{}\t{}{}".format(
                self.params["rubr_id"], self.params["language"], threshold, self.params["version"],
                os.linesep
            ))
        result_series = data_to_save.loc[0, "result"]
        if result_series is None:
            file.write("{}{}".format("REJECT", os.linesep))
        else:
            result_series = result_series[result_series > threshold]
            if len(result_series.index) == 0:
                file.write("{}{}".format("EMPTY", os.linesep))
            else:
                for topic in result_series.index:
                    proba = result_series.loc[topic]
                    if proba > threshold:
                        file.write("{}\t{}{}".format(topic, proba, os.linesep))
        if close_file:
            dest_file.close()

    def toDict(self):
        return self.data.to_dict()

    def getPredict(self):
        return self.data

    def setParams(self, lang=None, text_format=None, rubr_id=None, version=None):
        if lang is not None:
            self.params["language"] = lang
        if text_format is not None:
            self.params["format"] = lang
        if rubr_id is not None:
            self.params["rubr_id"] = rubr_id
        if version is not None:
            self.params["version"] = version

    def setPredict(self, predict: Series, lang: str, text_format: str, rubr_id: str, version):
        self.data = predict
        self.params["language"] = lang
        self.params["format"] = text_format
        self.params["rubr_id"] = rubr_id
        self.params["version"] = version