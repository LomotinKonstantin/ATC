from configparser import ConfigParser
import os.path
from pathlib import Path
import pandas as pd
from analyzer.modules.module import Module
import joblib
from sklearn.multiclass import OneVsRestClassifier


def read_model_and_md(path: str) -> tuple:
    assert os.path.exists(path)
    with open(path, "rb") as f:
        try:
            model = joblib.load(f)
            md = None
            md = joblib.load(f)
        except EOFError:
            print("\nERROR: Old classifier models are not supported anymore!\n")
            exit(0)
    return model, md


def read_md(path: str) -> tuple:
    assert os.path.exists(path)
    with open(path, "rb") as f:
        try:
            # Пропускаем модель
            joblib.load(f)
            md = None
            md = joblib.load(f)
        except (EOFError, ModuleNotFoundError):
            print("\nERROR: Old classifier models are not supported anymore!\n")
            exit(0)
    return md


class Classifier(Module):
    def __init__(self, rubr_id='SUBJ', lang='ru'):
        self.clf = None
        super().__init__("")
        self.rubr_id = rubr_id
        self.lang = lang
        self.config = self.loadConfig()
        self.loadClf()
        this_file = os.path.dirname(__file__)
        sect = "Settings"
        self.all_metadata = {
            opt: read_md(os.path.join(this_file, self.config.get(sect, opt)))
            for opt in self.config.options(sect)
        }
        # self.DEBUG = True

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
        file = os.path.dirname(__file__) + '/config.ini'
        if os.path.exists(file):
            config_parser.read(file)
        else:
            self.error_occurred.emit("Can't find the configuration file")
        return config_parser
    
    def loadClf(self):
        file = os.path.join(os.path.dirname(__file__),
                            self.config.get('Settings', self.rubr_id + '_' + self.lang))
        if os.path.exists(file):
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
