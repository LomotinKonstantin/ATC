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

        version = ""
        version += "p" + self.preprocessor.version
        version += "v" + self.vectorizer.version
        version += "c" + self.classifier.version
        self.version = self.config.get("App", "version") + version

    def analyze(self, text, params: dict) -> Predict:
        passed_lang = params["language"]
        rubr_id = params["rubricator_id"]
        passed_format = params["format"]
        norm_option = params["normalize"]
        self.info_message.emit("Предобработка...")
        if passed_lang == "auto":
            language = self.preprocessor.recognize_language(text=text, default="none")
            if language is None:
                self.error_occurred.emit("Не удалось распознать язык")
                return Predict(None,
                               lang="unknown",
                               rubr_id=rubr_id,
                               version=self.version,
                               text_format=passed_format,
                               normalize=norm_option)
            else:
                self.info_message.emit("Автоопределенный язык: " + language)
        else:
            language = passed_lang
        if not self.classifier.is_model_exist(rubr_id=rubr_id, lang=language):
            self.error_occurred.emit(
                f"Файл модели для языка \"{language}\" и рубрикатора \"{rubr_id}\" не найден"
            )
            return Predict(None,
                           lang=language,
                           rubr_id=rubr_id,
                           version=self.version,
                           text_format=passed_format,
                           normalize=norm_option)
        if passed_format == "auto":
            text_format = self.preprocessor.recognize_format(text)
            self.info_message.emit("Автоопределенный формат: {}".format(
                self.preprocessor.decode_format(text_format)))
        else:
            text_format = passed_format
        processed_text = self.preprocessor.process(text, language, text_format)
        # lang = language[:2]
        # if lang not in self.config.get(self.config_section, "languages"):
        #     self.error_occurred.emit(
        #         "Язык {} не поддерживается. Укажите язык текста на панели справа".format(language))
        #     return None
        vector_list = []
        result_list = []
        self.info_message.emit("Векторизация и классификация...")
        pooling = self.classifier.pooling_type(rubr_id=rubr_id.lower(),
                                               lang=language.lower())
        reject_threshold = self.vectorizer.rejectThreshold(pooling)
        for n, i in enumerate(processed_text.index):
            vector_i = self.vectorizer.vectorize(
                text=processed_text.loc[i, "text"],
                convolution=pooling,
                lang=language
            )
            if all(abs(i) < reject_threshold for i in vector_i):
                vector_i = None
                result_i = None
            else:
                result_i = self.classifier.classify(vector_i, language, rubr_id).round(5)
            vector_list.append(vector_i)
            result_list.append(result_i)
        processed_text["vector"] = Series(vector_list, index=processed_text.index)
        processed_text["result"] = Series(result_list, index=processed_text.index)
        predict = Predict(processed_text,
                          lang=language,
                          rubr_id=rubr_id,
                          version=self.version,
                          text_format=text_format,
                          normalize=norm_option)
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
