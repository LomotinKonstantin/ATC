import os
import sys
from importlib import import_module
from collections import OrderedDict
from json import loads

from PyQt5.QtCore import QObject, pyqtSignal
from pandas import Series, DataFrame


class Analyzer(QObject):
    import_error_occurred = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    eps = 1

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.preprocessor_path = sys.path[0] + "/modules/preprocessor"
        self.vectorizer_path = sys.path[0] + "/modules/word_embedding"
        self.classifier_path = sys.path[0] + "/modules/classifier"
        self.preprocessor = None
        self.vectorizer = None
        self.classifier = None
        self.version = ""

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

    def available_modules(self, module_path, meta=True):
        """
        :param meta: if True, returns OrderedDict with module and metadata
        :param module_path: one of the Analyzer.preprocessor_path, Analyzer.vectorizer_path or
                Analyzer.classifier_path
        :return: list or OrderedDict of available modules
        """
        dirs = self.dirs(module_path)
        if meta:
            res = OrderedDict()
            for module in dirs:
                try:
                    json_string = open(os.path.join(module_path, module, "metadata.json"),
                                       encoding="utf-8").read()
                    metadata = loads(json_string, object_pairs_hook=OrderedDict)
                except:
                    metadata = ""
                res[module] = metadata
            return res
        else:
            return dirs

    def load_modules(self, params, error_stream=None):
        preproc_module = self.config.get(self.config.PREPROC_OPTION)
        # format = params["format"]
        lang = params["language"]
        rubr_id = params["rubricator_id"]
        version = ""
        try:
            preprocessor = import_module("modules.preprocessor." +
                                         preproc_module + ".interface")
            preprocessor_class = getattr(preprocessor, "Preprocessor")
            self.preprocessor = preprocessor_class(lang)
            if error_stream:
                self.preprocessor.error_occurred.connect(error_stream)
            version += "p" + self.preprocessor.version
        except Exception as e:
            self.import_error_occurred.emit("Не удалось загрузить предобработчик \"{}\"\nОшибка: {}".format(
                preproc_module, e
            ))
            return False
        we_module = self.config.get(self.config.WE_OPTION)
        try:
            we = import_module("modules.word_embedding." + we_module + ".interface")
            we_class = getattr(we, "WordEmbedding")
            self.vectorizer = we_class(lang)
            if error_stream:
                self.vectorizer.error_occurred.connect(error_stream)
            version += "v" + self.vectorizer.version
        except Exception as e:
            self.import_error_occurred.emit("Не удалось загрузить векторайзер \"{}\"\nОшибка: {}".format(
                we_module, e
            ))
            return False
        class_module = self.config.get(self.config.CLASSIFIER_OPTION)
        try:
            classifier = import_module("modules.classifier." + class_module + ".interface")
            classifier_class = getattr(classifier, "Classifier")
            self.classifier = classifier_class(rubr_id, lang)
            if error_stream:
                self.classifier.error_occurred.connect(error_stream)
            version += "c" + self.classifier.version
        except Exception as e:
            self.import_error_occurred.emit("Не удалось загрузить классификатор \"{}\"\nОшибка: {}".format(
                class_module, e
            ))
            return False
        self.version = self.config.get(self.config.VERSION_OPTION) + version
        return True

    def analyze(self, text, progress_dialog=None):
        if progress_dialog is not None:
            progress_dialog.update_state(2, "Предобрабатываем текст...")
        processed_text = self.preprocessor.process(text)
        vector_list = []
        result_list = []
        for n, i in enumerate(processed_text.index):
            if progress_dialog is not None:
                progress_dialog.update_state(3, "Преобразуем текст в вектор... {}/{}".format(
                    n + 1, len(processed_text.index)
                ))
            vector_i = self.vectorizer.vectorize(
                processed_text.loc[i, "text"]
            )
            if all(abs(i) < self.eps for i in vector_i):
                vector_i = None
                result_i = None
                if progress_dialog is not None:
                    progress_dialog.update_state(3, "Не удалось определить рубрики... {}/{}".format(
                        n + 1, len(processed_text.index)
                    ))
            else:
                if progress_dialog is not None:
                    progress_dialog.update_state(3, "Классифицируем... {}/{}".format(
                        n + 1, len(processed_text.index)
                    ))
                result_i = self.classifier.classify(vector_i).round(3)
            vector_list.append(vector_i)
            result_list.append(result_i)
        processed_text["vector"] = Series(vector_list, index=processed_text.index)
        processed_text["result"] = Series(result_list, index=processed_text.index)
        return processed_text

    def export(self, result: DataFrame, filename, params):
        file = open(filename, "w", encoding="cp1251")
        # If result has 'multidoc' format
        if result.index.name == "id":
            file.write("{}\t{}\t{}\t{}\t{}\t{}\t{}{}".format(
                "id", "result", "rubricator", "language", "threshold", "version", "correct",
                os.linesep
            ))
            for i in result.index:
                class_result = result.loc[i, "result"]
                if class_result is not None:
                    class_result = class_result[class_result > params["threshold"]]
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
                    params["language"], params["threshold"], self.version, "###",
                    os.linesep
                ))
        # Apparently, else
        else:
            file.write("#\t{}\t{}\t{}\t{}{}".format(
                params["rubricator_id"], params["language"], params["threshold"], self.version,
                os.linesep
            ))
            for topic, proba in result.loc[0, "result"].items():
                if proba > params["threshold"]:
                    file.write("{}\t{}{}".format(topic, proba, os.linesep))
        file.close()

    def valid(self, text: str):
        if not text:
            return False
        if text.strip() == "":
            return False
        return True
