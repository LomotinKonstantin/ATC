from configparser import ConfigParser
from pathlib import Path
import pandas as pd
from analyzer.modules.module import Module
import joblib
from sklearn.multiclass import OneVsRestClassifier


def read_model_and_md(path: Path) -> tuple:
    if not path.exists():
        print(f"Model {path} does not exist")
    with open(path, "rb") as f:
        try:
            model = joblib.load(f)
            md = None
            md = joblib.load(f)
        except (EOFError, ModuleNotFoundError):
            print("\nERROR: Old classifier models are not supported anymore!\n")
            exit(0)
    return model, md


def read_metadata(path: Path) -> dict:
    _, md = read_model_and_md(path)
    return md


class Classifier(Module):

    all_metadata = None

    def __init__(self, rubr_id='SUBJ', lang='ru'):
        self.clf = None
        super().__init__("")
        self.rubr_id = rubr_id
        self.lang = lang
        self.config = self.loadConfig()
        # При первой загрузке будет происходить инициализация
        if self.all_metadata is None:
            self._init_all_metadata(self.config)
        self.clf_metadata = None
        self.loadClf()

    def _init_all_metadata(self, config: ConfigParser):
        self.all_metadata = {}
        for section in config.sections():
            if not section.startswith("Rubr"):
                continue
            code = config.get(section, "code", fallback="")
            if not code:
                continue
            for model_lang in ("ru", "en"):
                model_option = f"{model_lang}_model"
                if model_option not in config.options(section):
                    continue
                model_file = config.get(section, model_option, fallback="")
                if not model_file:
                    continue
                key = f"{code}_{model_lang}".lower()
                model_file = Path(__file__).parent / model_file
                self.all_metadata[key] = read_metadata(model_file)
                self.all_metadata[key]["model_fname"] = str(model_file.absolute())
                self.all_metadata[key]["display_name"] = config.get(section, "name", fallback=code)

    # Если lang == None, использует последний установленный язык.
    # Иначе обновляет текущий язык.
    def classify(self, vector, lang=None, rubr_id=None):
        if lang is not None:
            if self.lang != lang:
                self.lang = lang
                self.loadClf()
        if rubr_id is not None:
            if self.rubr_id != rubr_id:
                self.rubr_id = rubr_id
                self.loadClf()
        if self.clf is not None:
            has_good_coef_vec = hasattr(self.clf, 'coef_') and self.clf.coef_.T.shape[0] == len(vector)
            if (not hasattr(self.clf, 'coef_')) or has_good_coef_vec:
                if type(self.clf) == OneVsRestClassifier:
                    res = []
                    for i in self.clf.estimators_:
                        res.append((i.predict_proba([vector]))[0][1])
                    result = pd.Series(res, index=self.clf.classes_)
                    result = result.sort_values(ascending=False)
                else:
                    result = pd.Series(self.clf.predict_proba([vector])[0], index=self.clf.classes_)
                    result = result.sort_values(ascending=False)
                return result
            else:
                err_msg = f'Input vector has len {len(vector)}. Model requires {self.clf.coef_.T.shape[0]}.'
                self.error_occurred.emit(err_msg)
                return None
        else:
            return None

    def loadConfig(self): 
        config_parser = ConfigParser()
        file = Path(__file__).parent / 'config.ini'
        if file.exists():
            config_parser.read(str(file))
        else:
            self.error_occurred.emit("Can't find the configuration file")
        return config_parser
    
    def loadClf(self):
        assert self.all_metadata is not None
        key = f"{self.rubr_id}_{self.lang}".lower()
        file = Path(self.all_metadata[key]["model_fname"])
        if file.exists():
            self.clf, self.clf_metadata = read_model_and_md(file)
        else:
            self.error_occurred.emit("The classifier does not exist.")
            self.clf = None
            
    # Language setter. Reloads classifier immediately.
    def setLang(self, lang):
        self.lang = lang
        self.loadClf()
        
    def getLang(self):
        return self.lang

    def pooling_type(self, rubr_id: str, lang: str) -> str:
        """
        Тип пулинга матрицы текста, использовавшийся при обучении модели.
        Одно из mean, max, sum
        :return:
        """
        settings = self.all_metadata[f"{rubr_id}_{lang}"]
        return settings["pooling"]

    def is_model_exist(self, rubr_id: str, lang: str) -> bool:
        if lang is not None and lang != "auto":
            ret = f"{rubr_id}_{lang}".lower() in self.all_metadata
        else:
            ret = rubr_id.lower() in self.installed_rubricators()
        return ret

    def installed_rubricators(self) -> list:
        ids = ("_".join(k.split("_")[:-1]) for k in self.all_metadata)
        return list(set(ids))
