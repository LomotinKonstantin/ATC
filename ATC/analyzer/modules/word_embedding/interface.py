import warnings
warnings.filterwarnings(action='ignore')
from gensim.models import Word2Vec
from configparser import ConfigParser
import numpy as np
import os.path
from analyzer.modules.module import Module


class WordEmbedding(Module):
    def __init__(self, lang='ru'):
        super().__init__(os.path.dirname(__file__) + "\\metadata.json")
        self.lang = lang
        self.config = self.loadConfig()
        self.loadModel()

    # If lang == None, creates vector according to last set language.
    # If lang != None, checks if input language corresponds with model language 
    # before creating vectors. If it does not, set new model language and changes model.
    # Language can be set in constructor, vectorize(self, text, lang) function
    # or with setter.
    def vectorize(self, text, convolution: str, lang=None):
        if lang:
            if self.lang != lang:
                self.lang = lang
                self.loadModel()
        if self.model:
            tokens = text.split()
            features = [0]*self.length
            if convolution == 'sum':
                for t in tokens:
                    if t in self.model:
                        features += self.model[t]
            elif convolution in ['max', 'mean']:
                for t in tokens:
                    if t in self.model:
                        features = np.vstack((features, self.model[t]))
                if features.shape[0] > 1:
                    if convolution == 'max':
                        features = features.max(axis=0)
                    else:
                        features = features.mean(axis=0)
            return features
        else:
            return None
        
    def loadModel(self):
        file = os.path.join(os.path.dirname(__file__), self.config.get('Settings', self.lang))
        if os.path.exists(file):
            self.model = Word2Vec.load(file)
            self.length = self.model.layer1_size
        else:
            self.error_occurred.emit('The W2V model does not exist.')
            self.model = None

    def loadConfig(self): 
        config_parser = ConfigParser()
        file = os.path.dirname(__file__) + '/config.ini'
        if os.path.exists(file):
            config_parser.read(file)
        else:
            self.error_occurred.emit("Can't find the configuration file.")
        return config_parser

    def rejectThreshold(self, pooling: str):
        return float(self.config.get("Settings", f"reject_threshold_{pooling}"))
    
    # Language setter. Reloads the model immediately.
    def setLang(self, lang):
        self.lang = lang
        self.loadModel()
        
    def getLang(self):
        return self.lang
