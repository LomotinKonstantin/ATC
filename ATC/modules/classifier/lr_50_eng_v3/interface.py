from configparser import ConfigParser
import sys
import os.path
import pandas as pd
from modules.common import Module
from sklearn.externals import joblib


class Classifier(Module):
    def __init__(self, rubr_id='SUBJ', lang='ru'):
        super().__init__(os.path.dirname(__file__) + "\\metadata.json")
        self.rubr_id = rubr_id
        self.lang = lang
        self.config = self.loadConfig()
        self.loadClf()
        
    # If lang == None, classifies vector according to last set language.
    # If lang != None, checks if input language corresponds with current language 
    # before classification. If it does not, set new current language and changes classifier.       
    # Language can be set in constructor, classify(self, text, lang) function
    # or with setter.
    def classify(self, vector, lang = None):
        if lang:
            if self.lang != lang:
                self.lang = lang
                self.loadClf()            
        if self.clf:
            if self.clf.coef_.T.shape[0] == len(vector):
                result = pd.Series(self.clf.predict_proba([vector])[0], index=self.clf.classes_)
                result = result.sort_values(ascending=False)
                # result = result.round(3)
                # result = result[result!=0]
                return result   
            else:
                self.error_occurred.emit('Vector has '+str(len(vector))+' elements. Model can work with vectors that have '+str(clf.coef_.T.shape[0])+'attibutes.')
                return None
        else:
            return None   
    
     
    def loadConfig(self): 
        configParcer = ConfigParser()
        file = os.path.dirname(__file__) + '/config.ini'
        if os.path.exists(file):
            configParcer.read(file)
        else:
            self.error_occurred.emit("Can't find the configuration file")
        return configParcer    
    
    def loadClf(self):
        file = os.path.join(os.path.dirname(__file__),
                            self.config.get('Settings', self.rubr_id+'_'+self.lang))
        if os.path.exists(file):
            self.clf = joblib.load(file)
        else:
            self.error_occurred.emit("The classifier does not exist.")
            self.clf = None
            
    # Language setter. Reloads classifier immediately.
    def setLang(lang):
        self.lang = lang
        self.loadClf()
        
    def getLang():
        return self.lang    
