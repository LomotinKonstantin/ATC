import os

from PyQt5.QtCore import QObject, pyqtSignal
from pandas import Series, DataFrame

from analyzer.modules.preprocessor.interface import Preprocessor
from analyzer.modules.word_embedding.interface import WordEmbedding
from analyzer.modules.classifier.interface import Classifier
from common.predict import Predict


class Analyzer(QObject):
    error_occurred = pyqtSignal(str)
    language_recognized = pyqtSignal(str, bool)
    config_section = "AvailableOptions"

    ###
    ### TODO: add moar signals for each operation (preprocessing, w2v, classification)
    ###

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.preprocessor = None
        self.vectorizer = None
        self.classifier = None
        self.version = ""
        self.eps = 0
        self.last_language = None
        self.load_modules()

    def load_file(self, filename):
        file = open(filename, encoding="cp1251")
        content = file.read()
        return content

    def dirs(self, path):
        files = os.listdir(path)
        res = []
        for i in files:
            file = os.path.join(path, i)
            if os.path.isdir(file) and i != "__pycache__":
                res.append(i)
        return res

    ###
    ### TODO: make modules multi-usable (not to load them each time)
    ###

    def load_modules(self):
        self.preprocessor = Preprocessor()
        self.vectorizer = WordEmbedding()
        self.classifier = Classifier()

        self.eps = float(self.vectorizer.rejectThreshold())
        version = ""
        version += "p" + self.preprocessor.version
        version += "v" + self.vectorizer.version
        version += "c" + self.classifier.version
        self.version = self.config.get(self.config.VERSION_OPTION) + version


    def analyze(self, text, params: dict):
        lang = params["language"]
        auto = lang == "auto"
        processed_text, language = self.preprocessor.process(text, lang)
        lang = language[:2]
        predict = Predict()
        predict.setParams(lang=lang)

        if lang not in self.config.get(""):
            self.error_occurred.emit(
                "Язык {} не поддерживается. Укажите язык текста на панели справа".format(language))
            return None
        predict = Predict()
        vector_list = []
        result_list = []
        for n, i in enumerate(processed_text.index):
            vector_i = self.vectorizer.vectorize(
                processed_text.loc[i, "text"],
                language
            )
            # print(processed_text.loc[i, "text"], vector_i)
            if all(abs(i) < self.eps for i in vector_i):
                vector_i = None
                result_i = None
            else:
                result_i = self.classifier.classify(vector_i, lang).round(3)
            vector_list.append(vector_i)
            result_list.append(result_i)
        processed_text["vector"] = Series(vector_list, index=processed_text.index)
        processed_text["result"] = Series(result_list, index=processed_text.index)
        return processed_text

    def export(self, result: DataFrame, filename, params):
        file = open(filename, "w", encoding="cp1251")
        # If result has 'multidoc' format
        threshold = round(params["threshold"], 2)
        if result.index.name == "id":
            file.write("{}\t{}\t{}\t{}\t{}\t{}\t{}{}".format(
                "id", "result", "rubricator", "language", "threshold", "version", "correct",
                os.linesep
            ))
            for i in result.index:
                class_result = result.loc[i, "result"]
                if class_result is not None:
                    class_result = class_result[class_result > threshold]
                    if len(class_result.index) > 0:
                        result_str = "\\".join(
                            ["{}-{}".format(j, class_result.loc[j]) for j in class_result.index]
                        )
                    else:
                        result_str = "EMPTY"
                else:
                    result_str = "REJECT"
                file.write("{}\t{}\t{}\t{}\t{}\t{}\t{}{}".format(
                    i, result_str, params["rubricator_id"],
                    self.last_language, threshold, self.version, "###",
                    os.linesep
                ))
        # Apparently, if format is 'plain' or 'divided'
        else:
            file.write("#\t{}\t{}\t{}\t{}{}".format(
                params["rubricator_id"], params["language"], threshold, self.version,
                os.linesep
            ))
            result_series = result.loc[0, "result"]
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
        file.close()

    def isTextValid(self, text: str):
        if not text:
            return False
        if text.strip() == "":
            return False
        return True

