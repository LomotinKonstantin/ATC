from configparser import ConfigParser
import sys
import os.path
import pandas as pd
# sys.path.append("..")
from modules.common import Module
from sklearn.externals import joblib


class Classifier(Module):
    def __init__(self, rubr_id='SUBJ', lang='ru'):
        super().__init__()
        self.rubr_id = rubr_id
        self.lang = lang
        self.config = self.loadConfig()
        self.loadClf()
        
    def classify(self, vector):
        if self.clf:
            result = pd.Series(self.clf.predict_proba([vector])[0], index=self.clf.classes_)
            result = result.sort_values(ascending=False)
            # result = result.round(3)
            # result = result[result!=0]
            return result   
        else:
            return None        
        
    def loadConfig(self): 
        configParcer = ConfigParser()
        configParcer.read(os.path.dirname(__file__) + '/config.ini')
        return configParcer    
    
    def loadClf(self):
        file = os.path.join(os.path.dirname(__file__),
                            self.config.get('Settings', self.rubr_id+'_'+self.lang))
        if os.path.exists(file):
            self.clf = joblib.load(file)
        else:
            self.clf = None
