import json
from collections import OrderedDict


class Module:

    def __init__(self, filename="./metadata.json"):
        self._load_metadata(filename)

    def _load_metadata(self, filename):
        json_string = open(filename, encoding="utf-8").read()
        self.metadata = json.loads(json_string, object_pairs_hook=OrderedDict)
