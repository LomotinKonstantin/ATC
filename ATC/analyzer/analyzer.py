from PyQt5.QtCore import QThread, pyqtSignal
from pandas import Series

from analyzer.modules.preprocessor.interface import Preprocessor
from analyzer.modules.word_embedding.interface import WordEmbedding
from analyzer.modules.classifier.interface import Classifier
from common.predict import Predict

###
### TODO: refactor
###


class Analyzer(QThread):
    error_occurred = pyqtSignal(str)
    info_message = pyqtSignal(str)
    warning_message = pyqtSignal(str)
    complete = pyqtSignal(Predict)

    config_section = "AvailableOptions"

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
        self.text = None
        self.params = None

    def load_file(self, filename):
        file = open(filename, encoding="cp1251")
        content = file.read()
        return content

    def load_modules(self):
        self.preprocessor = Preprocessor()
        self.vectorizer = WordEmbedding()
        self.classifier = Classifier()

        self.preprocessor.error_occurred.connect(self.error_occurred)
        self.vectorizer.error_occurred.connect(self.error_occurred)
        self.classifier.error_occurred.connect(self.error_occurred)

        self.eps = float(self.vectorizer.rejectThreshold())
        version = ""
        version += "p" + self.preprocessor.version
        version += "v" + self.vectorizer.version
        version += "c" + self.classifier.version
        self.version = self.config.get("App", "version") + version

    def analyze(self, text, params: dict):
        passed_lang = params["language"]
        rubr_id = params["rubr_id"]
        passed_format = params["format"]
        self.info_message.emit("Предобработка...")
        if passed_lang == "auto":
            language = self.preprocessor.recognize_language(text=text, default="none")
            if language is None:
                self.error_occurred.emit("Не удалось распознать язык")
                return None
            else:
                self.info_message.emit("Автоопределенный язык: " + language)
        else:
            language = passed_lang
        if passed_format == "auto":
            text_format = self.preprocessor.recognize_format(text)
            text_format = self.preprocessor.encode_format(text_format)
        else:
            text_format = passed_format
        processed_text = self.preprocessor.process(text, language)
        # lang = language[:2]
        # if lang not in self.config.get(self.config_section, "languages"):
        #     self.error_occurred.emit(
        #         "Язык {} не поддерживается. Укажите язык текста на панели справа".format(language))
        #     return None
        vector_list = []
        result_list = []
        self.info_message.emit("Векторизация и классификация...")
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
                result_i = self.classifier.classify(vector_i, language, rubr_id).round(3)
            vector_list.append(vector_i)
            result_list.append(result_i)
        processed_text["vector"] = Series(vector_list, index=processed_text.index)
        processed_text["result"] = Series(result_list, index=processed_text.index)
        predict = Predict(processed_text,
                          lang=language,
                          rubr_id=rubr_id,
                          version=self.version,
                          text_format=text_format)
        self.complete.emit(predict)
        return predict

    def run(self):
        try:
            self.analyze(self.text, self.params)
        except Exception as e:
            print(e)

    def analyzeInParallel(self, text, params: dict):
        """
        Launches classification in a separate thread. Result is contained in the 'complete()'
        signal.
        :param text: text to process
        :param params: user options
        """
        self.text = text
        self.params = params
        self.start()

    def isTextValid(self, text: str):
        if text is None:
            return False
        if text.strip() == "":
            return False
        return True

