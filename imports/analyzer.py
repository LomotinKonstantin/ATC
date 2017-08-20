import os
import sys
from importlib import import_module
from collections import OrderedDict
from json import loads

from PyQt5.QtCore import QObject, pyqtSignal
from pandas import Series


class Analyzer(QObject):

    import_error_occurred = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.preprocessor_path = sys.path[0] + "/modules/preprocessor"
        self.vectorizer_path = sys.path[0] + "/modules/word_embedding"
        self.classifier_path = sys.path[0] + "/modules/classifier"
        self.preprocessor = None
        self.vectorizer = None
        self.classifier = None

    def load_file(self, filename):
        file = open(filename)
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

    def load_modules(self, params, error_slot=None):
        preproc_module = self.config.get(self.config.PREPROC_OPTION)
        format = params["format"]
        lang = params["language"]
        rubr_id = params["rubricator_id"]
        # try:
        preprocessor = import_module("modules.preprocessor." +
                                     preproc_module + ".interface")
        preprocessor_class = getattr(preprocessor, "Preprocessor")
        self.preprocessor = preprocessor_class(format, lang)
        self.preprocessor.error_occurred.connect(error_slot)
        # except:
        #     self.import_error_occurred.emit("Не удалось загрузить предобработчик \"" +
        #                                     preproc_module + "\"!")
        #     return False
        we_module = self.config.get(self.config.WE_OPTION)
        # try:
        we = import_module("modules.word_embedding." + we_module + ".interface")
        we_class = getattr(we, "WordEmbedding")
        self.vectorizer = we_class(lang)
        self.vectorizer.error_occurred.connect(error_slot)
        # except:
        #     self.import_error_occurred.emit("Не удалось загрузить векторайзер \"" +
        #                                     we_module + "\"!")
        #     return False
        class_module = self.config.get(self.config.CLASSIFIER_OPTION)
        try:
            classifier = import_module("modules.classifier." + class_module + ".interface")
            classifier_class = getattr(classifier, "Classifier")
            self.classifier = classifier_class(rubr_id, lang)
            self.classifier.error_occurred.connect(error_slot)
        except:
            self.import_error_occurred.emit("Не удалось загрузить классификатор \"" +
                                            class_module + "\"!")
            return False
        # if error_slot:
        #     for i in [preprocessor_class, we_class, classifier_class]:
        #         print(i.error_occurred)
        #         i.error_occurred.connect(error_slot)
        return True

    # TODO add signals
    def analyze(self, text):
        processed_text = self.preprocessor.process(text)
        vector = self.vectorizer.vectorize(processed_text)
        result = self.classifier.classify(vector)
        return result.round(3)

    def export(self, result, filename):
        file = open(filename, "w")
        if isinstance(result, dict):
            for i, j in result.items():
                file.write("{}\t{}\n".format(i, j))
        elif isinstance(result, str):
            file.write(result)
        elif isinstance(result, Series):
            for topic, proba in result.iteritems():
                file.write("{}\t{}\n".format(topic, proba))

