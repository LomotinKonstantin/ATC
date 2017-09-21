from gensim.models import Word2Vec
from configparser import ConfigParser
import numpy as np
import os.path
import sys 
# sys.path.append("..")
from modules.common import Module


class WordEmbedding(Module):
    def __init__(self, lang='ru'):
        super().__init__(os.path.dirname(__file__) + "\\metadata.json")
        self.lang = lang
        self.config = self.loadConfig()
        self.loadModel()
        self.length = self.model.layer1_size  # ������ ������� ����������.

    def vectorize(self, text):
        if self.model:
            features = np.zeros((1, self.length))
            # �������� ������ ����.
            tokens = text.split()
            # � ����������� �� ���� ������� �������� ������ ���������.
            if self.config.get('Settings', 'convolution') == 'sum':
                for t in tokens:
                    if t in self.model:
                        features += self.model[t]
            elif self.config.get('Settings', 'convolution') == 'max':
                for t in tokens:
                    if t in self.model:
                        features = np.vstack((features, self.model[t]))
                if features.shape[0] > 1:
                    features = features.max(axis=0)
                features = [features]
            return features[0]
        else:
            return None
        
    def loadModel(self):
        file = os.path.join(os.path.dirname(__file__), self.config.get('Settings', self.lang))
        if os.path.exists(file):
            self.model = Word2Vec.load(file)
        else:
            self.error_occurred.emit('Model does not exists.')
            self.model = None

    def loadConfig(self): 
        configParcer = ConfigParser()
        file = os.path.dirname(__file__) + '/config.ini'
        if os.path.exists(file):
            configParcer.read(file)
        else:
            self.error_occurred.emit("Can't find the configuration file.")
        return configParcer

    def rejectThreshold(self):
        return self.config.get("Settings", "reject_threshold")
