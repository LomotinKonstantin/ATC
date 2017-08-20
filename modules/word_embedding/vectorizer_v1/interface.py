from gensim.models import Word2Vec
from configparser import ConfigParser
import numpy as np
import os.path
import sys 
sys.path.append("..")
from common import Module

class WordEmbedding(Module):
    def __init__(self, lang='ru'):
        super().__init__()
        self.lang = lang
        self.config = self.loadConfig()
        self.loadModel()
        self.lenght = self.model.layer1_size # Размер вектора результата.
        
    def vectorize(self, text):
        if self.model:
            features = np.zeros((1,self.lenght))
            # Создание списка слов.
            tokens = text.split()
            # В зависимости от типа свертки создание списка признаков.
            if self.config.get('Settings', 'convolution') == 'sum':
                for t in tokens:
                    if t in self.model:
                        features += self.model[t]
            elif self.config.get('Settings', 'convolution') == 'max':
                for t in tokens:
                    if t in self.model:
                        features = np.vstack((features, self.model[t]))
                if features.shape[0]>1:
                    features = features.max(axis=0)
                features = [features]
            return features[0]
        else:
            return None
        
    def loadModel(self):
        if os.path.exists(self.config.get('Settings', self.lang)):
            self.model = Word2Vec.load(self.config.get('Settings', self.lang))
        else:
            self.model = None          
        
    def loadConfig(self): 
        configParcer = ConfigParser()
        configParcer.read('config.ini')
        return configParcer
        