from configparser import ConfigParser
import os.path
import pandas as pd
from analyzer.modules.module import Module
import joblib
from sklearn.multiclass import OneVsRestClassifier


def read_model_and_md(path: str) -> tuple:
    assert os.path.exists(path)
    with open(path, "rb") as f:
        model = joblib.load(f)
        md = None
        try:
            md = joblib.load(f)
        except EOFError:
            pass
    return model, md


class Classifier(Module):
    def __init__(self, rubr_id='SUBJ', lang='ru'):
        self.clf = None
        self.clf_metadata = None
        self.experiment_info = None
        super().__init__(os.path.dirname(__file__) + "\\metadata.json")
        self.rubr_id = rubr_id
        self.lang = lang
        self.config = self.loadConfig()
        self.loadClf()
        # self.DEBUG = True
        # Сейчас загружена метадата модели, можем выводить ее пользователю
        if self.clf_metadata is not None:
            for k, v in self.clf_metadata.items():
                if isinstance(v, dict):
                    continue
                self.metadata[k] = v
            self.experiment_info = self.clf_metadata["settings"]


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
                            self.config.get('Settings', self.rubr_id+'_'+self.lang))
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
