import os
from importlib import import_module

from PyQt5.QtCore import QObject, pyqtSignal


class Analyzer(QObject):

    import_error_occured = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.preprocessor_path = "modules/preprocessor"
        self.vectorizer_path = "modules/wordembedding"
        self.classifier_path = "modules/classifier"
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
            if os.path.isdir(file):
                res.append(i)
        return res

    def available_preprocessors(self):
        return self.dirs(self.preprocessor_path)

    def load_modules(self, params, error_slot=None):
        preproc_module = self.config.get(self.config.PREPROC_OPTION)
        format = params["format"]
        lang = params["language"]
        rubr_id = params["rubricator_id"]
        try:
            preprocessor = import_module("modules.preprocessor." +
                                         preproc_module + ".interface")
            preprocessor_class = getattr(preprocessor, "Preprocessor")
            self.preprocessor = preprocessor_class(format, lang)
        except ImportError:
            self.import_error_occured.emit("Не удалось загрузить предобработчик \"" +
                                           preproc_module + "\"!")

        we_module = self.config.get(self.config.WE_OPTION)
        try:
            we = import_module("modules.wordembedding." + we_module + ".interface")
            we_class = getattr(we, "WordEmbedding")
            self.vectorizer = we_class(lang)
        except ImportError:
            self.import_error_occured.emit("Не удалось загрузить векторайзер \"" +
                                           we_module + "\"!")

        class_module = self.config.get(self.config.CLASSIFIER_OPTION)
        try:
            classifier = import_module("modules.classifier." + class_module + ".interface")
            classifier_class = getattr(classifier, "Classifier")
            self.classifier = classifier_class(rubr_id, lang)
        except ImportError:
            self.import_error_occured.emit("Не удалось загрузить классификатор \"" +
                                           class_module + "\"!")

        if error_slot:
            for i in [self.preprocessor, self.vectorizer, self.classifier]:
                i.error_occured.connect(error_slot)

    def analyze(self, text):
        processed_text = self.preprocessor.process(text)
        return {"result" : processed_text.loc[0, "text"]}

    def export(self, result, filename):
        file = open(filename, "w")
        if isinstance(result, dict):
            for i, j in result.items():
                file.write("{}\t{}".format(i, j))
        else:
            file.write(result)

