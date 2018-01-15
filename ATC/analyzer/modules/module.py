###
### TODO: implement parent class
###
import os
import json
from collections import OrderedDict
from configparser import ConfigParser

from PyQt5.QtCore import pyqtSignal, QObject


class Module(QObject):

    # Emit this signal with error message when smth goes wrong
    error_occurred = pyqtSignal(str)

    # Use self.metadata field to access OrderedDict with metadata
    def __init__(self, filename="metadata.json"):
        super().__init__()
        self.metadata = self.loadMetadata(filename)
        self.version = str(self.metadata["Версия"])

    def loadMetadata(self, filename):
        try:
            json_string = open(filename, encoding="utf-8").read()
            metadata = json.loads(json_string, object_pairs_hook=OrderedDict)
        except IOError:
            self.error_occurred.emit("Error loading metadata")
            metadata = {}
        return metadata

    def loadConfig(self):
        configParcer = ConfigParser()
        file = os.path.join(os.path.dirname(__file__), 'config.ini')
        if os.path.exists(file):
            configParcer.read(file)
        else:
            self.error_occurred.emit("Can't find the configuration file.")
        return configParcer