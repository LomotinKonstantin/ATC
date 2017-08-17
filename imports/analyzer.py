import os
from importlib import import_module

from PyQt5.QtCore import QObject, pyqtSignal


class Analyzer(QObject):

    import_error_occured = pyqtSignal(str)

    def __init__(self, config, params={}):
        super().__init__()
        self.config = config
        self.params = params
        self.preprocessor_path = "modules/preprocessor"
        # loading modules TODO
        preproc_module = config.get(config.PREPROC_OPTION)
        preprocessor = import_module("modules.preprocessor." + preproc_module + ".interface")
        preprocessor_class = getattr(preprocessor, "Preprocessor")
        self.preprocessor = preprocessor_class("", "")

    def set_parameters(self, params):
        if not isinstance(params, dict):
            raise TypeError("Parameters must be a dict type")
        self.params = params

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

    def _load_module(self, import_str):
        try:
            import_module(import_str)
        except TypeError or ImportError:
            self.import_error_occured.emit(import_str)

    def analyze(self, text):
        processed_text = self.preprocessor.process(text)
        return processed_text
