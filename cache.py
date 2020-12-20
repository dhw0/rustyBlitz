import json
import os.path

class Cache():
    def __init__(self, path):
        self.path = path
        self.db = self._load_db(self.path)

    def _load_db(self, path):
        if(os.path.isfile(fname)):
            with open(path, 'r') as f:
                return json.load(f)
        else:
            return {}
    