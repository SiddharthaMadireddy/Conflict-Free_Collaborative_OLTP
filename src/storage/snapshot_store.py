import json, os

class SnapshotStore:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def save(self, data):
        with open(self.path, 'w') as f:
            json.dump(data, f, indent=2)

    def load(self):
        if not os.path.exists(self.path):
            return {}
        with open(self.path) as f:
            return json.load(f)
