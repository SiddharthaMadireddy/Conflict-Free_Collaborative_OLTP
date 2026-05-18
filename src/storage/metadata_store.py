import json, os
from src.core.constants import DEFAULT_FK_POLICY

class MetadataStore:
    def __init__(self, replica_dir):
        self.path = os.path.join(replica_dir, 'metadata.json')
        self._data = {'watermarks': {}, 'peers': [], 'fk_policy': None}
        os.makedirs(replica_dir, exist_ok=True)
        self._load()

    def get_watermarks(self):
        return dict(self._data.get('watermarks', {}))

    def update_watermark(self, actor_id, seq):
        self._data['watermarks'][actor_id] = max(self._data['watermarks'].get(actor_id, 0), seq)
        self._save()

    def merge_watermarks(self, incoming):
        for actor_id, seq in incoming.items():
            self.update_watermark(actor_id, seq)

    def set_fk_policy(self, policy):
        self._data['fk_policy'] = policy
        self._save()

    def get_fk_policy(self):
        return self._data.get('fk_policy') or DEFAULT_FK_POLICY

    def _save(self):
        with open(self.path, 'w') as f:
            json.dump(self._data, f, indent=2)

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path) as f:
                    content = f.read().strip()
                    if content:
                        self._data = json.loads(content)
            except Exception:
                pass

    def clear(self):
        self._data = {'watermarks': {}, 'peers': [], 'fk_policy': None}
        self._save()
