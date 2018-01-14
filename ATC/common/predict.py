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

    def __init__(self, predict: Series, lang: str, text_format: str, rubr_id: str, version: str):
        self.data = None
        self.language = None
        self.format = None
        self.rubr_id = None
        self.setPredict(predict, lang, text_format, rubr_id)
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
                self.rubr_id, self.language, threshold, self.version,
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

    def setPredict(self, predict: Series, lang: str, text_format: str, rubr_id: str):
        self.data = predict
        self.language = lang
        self.format = text_format
        self.rubr_id = rubr_id