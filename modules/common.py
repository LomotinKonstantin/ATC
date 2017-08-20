import json
from collections import OrderedDict
from PyQt5.QtCore import pyqtSignal, QObject


# TODO add config manager and path autodetection
class Module(QObject):

    # Emit this signal with error message when smth goes wrong
    error_occurred = pyqtSignal(str)

    # Use self.metadata field to access OrderedDict with metadata
    def __init__(self, filename="./metadata.json"):
        super().__init__()
        self._load_metadata(filename)

    def _load_metadata(self, filename):
        try:
            json_string = open(filename, encoding="utf-8").read()
            self.metadata = json.loads(json_string, object_pairs_hook=OrderedDict)
        except IOError:
            self.metadata = {}
