import os.path
import pandas as pd
from analyzer.modules.module import Module
from sklearn.externals import joblib


class Classifier(Module):
    def __init__(self):
        super().__init__(os.path.join(os.path.dirname(__file__), "metadata.json"))
        self.last_rubr_id = None
        self.last_lang = None
        self.clf = None
        self.config = self.loadConfig(__file__)

    # If lang == None, classifies vector according to last set language.
    # If lang != None, checks if input language corresponds with current language 
    # before classification. If it does not, set new current language and changes classifier.       
    # Language can be set in constructor, classify(self, text, lang) function
    # or with setter.
    def classify(self, vector, lang, rubr_id):
        if lang:
            if self.last_lang != lang or self.last_rubr_id != rubr_id:
                self.last_lang = lang
                self.last_rubr_id = rubr_id
                self.loadClf()
        if self.clf:
            if self.clf.coef_.T.shape[0] == len(vector):
                result = pd.Series(self.clf.predict_proba([vector])[0], index=self.clf.classes_)
                result = result.sort_values(ascending=False)
                return result
            else:
                self.error_occurred.emit(
                    'Vector has '+str(len(vector)) +
                    ' elements. The model requires vectors that have ' +
                    str(self.clf.coef_.T.shape[0])+' attributes.')
                return None
        else:
            return None   
    
    def loadClf(self):
        file = os.path.join(os.path.dirname(__file__),
                            self.config.get('Settings',
                                            '{0}_{1}'.format(self.last_rubr_id, self.last_lang)))
        if os.path.exists(file):
            clf = joblib.load(file)
        else:
            self.error_occurred.emit("The classifier model does not exist")
            clf = None
        return clf
            
    # Language setter. Reloads classifier immediately.
    def setLang(self, lang):
        self.last_lang = lang
        self.loadClf()

    def getLang(self):
        return self.lang    
