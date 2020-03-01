import os

import numpy as np


class Predict:
    """
    The class for storing classification result. Provides
    methods for different representations of the result.
    """

    def __init__(self, predict=None,
                 lang=None,
                 text_format=None,
                 rubr_id=None,
                 version=None,
                 normalize="not"):
        self.data = None
        self.params = {
            "language": None,
            "format": None,
            "rubr_id": None,
            "version": None,
            "normalize": "not",
        }
        self.setPredict(predict, lang, text_format, rubr_id, version,
                        normalize=normalize)
        return

    def normalize_probas(self, values):
        return values / sum(values)

    def save_to_file(self, filename, threshold=0, n_digits=3):
        """
        Saves the predict to the provided file
        :param threshold: probability threshold. All answers with lower proba will be rejected
        :param filename: filename
        :param n_digits: number of digits after the decimal point
        :return: None
        """
        file = open(filename, "w", encoding="cp1251")

        threshold = round(threshold, n_digits)
        # If data does not exist:
        if self.data is None:
            file.write(f"#\t{self.params['rubr_id']}\t"
                       f"{self.params['language']}\t"
                       f"{threshold}\t{self.params['version']}\t"
                       f"{self.params['normalize']}"
                       f"{os.linesep}")
            file.write("{}{}".format("REJECT", os.linesep))
            return 
        # If result has 'multidoc' format
        data_to_save = self.data.copy()
        if data_to_save.index.name == "id":
            file.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}{}".format(
                "id", "result", "rubricator", "language", "threshold", "version", "normalize", "correct",
                os.linesep
            ))
            for i in data_to_save.index:
                class_result = data_to_save.loc[i, "result"]
                if class_result is not None:
                    class_result = np.round(class_result, n_digits)
                    class_result = class_result[class_result >= threshold]
                    if self.params["normalize"] == "all":
                        class_result = self.normalize_probas(class_result)
                        class_result = np.round(class_result, n_digits)
                    elif self.params["normalize"] == "some":
                        if sum(class_result) > 1.:
                            class_result = self.normalize_probas(class_result)
                            class_result = np.round(class_result, n_digits)
                    if len(class_result.index) > 0:
                        result_str = "\\".join(
                            ["{}-{}".format(j, round(class_result.loc[j], n_digits))
                             for j in class_result.index]
                        )
                    else:
                        result_str = "EMPTY"
                else:
                    result_str = "REJECT"
                file.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}{}".format(
                    i, result_str, self.params["rubr_id"],
                    self.params["language"], threshold, self.params["version"],
                    self.params["normalize"], "###",
                    os.linesep
                ))
        # Apparently, if format is 'plain' or 'divided'
        else:
            file.write("#\t{}\t{}\t{}\t{}\t{}{}".format(
                self.params["rubr_id"], self.params["language"], threshold, self.params["version"],
                self.params["normalize"],
                os.linesep
            ))
            result_series = data_to_save.loc[0, "result"]
            if result_series is None:
                file.write("{}{}".format("REJECT", os.linesep))
            else:
                result_series = np.round(result_series, n_digits)
                result_series = result_series[result_series >= threshold]
                if self.params["normalize"] == "all":
                    result_series = self.normalize_probas(result_series)
                    result_series = np.round(result_series, n_digits)
                elif self.params["normalize"] == "some":
                    if sum(result_series) > 1.:
                        result_series = self.normalize_probas(result_series)
                        result_series = np.round(result_series, n_digits)
                if len(result_series.index) == 0:
                    file.write("{}{}".format("EMPTY", os.linesep))
                else:
                    for topic in result_series.index:
                        proba = round(result_series.loc[topic], n_digits)
                        if proba >= threshold:
                            file.write("{}\t{}{}".format(topic, proba, os.linesep))

    def getPredict(self):
        return self.data

    def setParams(self, lang=None, text_format=None, rubr_id=None, version=None, normalize="not"):
        if lang is not None:
            self.params["language"] = lang
        if text_format is not None:
            self.params["format"] = text_format
        if rubr_id is not None:
            self.params["rubr_id"] = rubr_id
        if version is not None:
            self.params["version"] = version
        self.params["normalize"] = normalize

    def setPredict(self, predict,
                   lang: str, text_format: str,
                   rubr_id: str, version, normalize: str):
        self.data = predict
        self.params["language"] = lang
        self.params["format"] = text_format
        self.params["rubr_id"] = rubr_id
        self.params["version"] = version
        self.params["normalize"] = normalize

    def getFormat(self):
        return self.params["format"]

    def getLanguage(self):
        return self.params["language"]

    def getRubrId(self):
        return self.params["rubr_id"]

    def getVersion(self):
        return self.params["version"]
