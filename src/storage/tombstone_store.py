import json, os

class TombstoneEntry:
    def __init__(self, row_id, table, actor_id, seq):
        self.row_id = row_id
        self.table = table
        self.actor_id = actor_id
        self.seq = seq

    def to_dict(self):
        return {'row_id': self.row_id, 'table': self.table, 'actor_id': self.actor_id, 'seq': self.seq}

    @classmethod
    def from_dict(cls, d):
        return cls(d['row_id'], d['table'], d['actor_id'], d['seq'])

class TombstoneStore:
    def __init__(self, replica_dir):
        self.path = os.path.join(replica_dir, 'tombstones.json')
        self._entries = {}
        os.makedirs(replica_dir, exist_ok=True)
        self._load()

    def _key(self, table, row_id):
        return f'{table}:{row_id}'

    def record(self, table, row_id, actor_id, seq):
        self._entries[self._key(table, row_id)] = TombstoneEntry(row_id, table, actor_id, seq)
        self._save()

    def all_entries(self):
        return list(self._entries.values())

    def remove(self, table, row_id):
        self._entries.pop(self._key(table, row_id), None)
        self._save()

    def _save(self):
        with open(self.path, 'w') as f:
            json.dump({k: v.to_dict() for k, v in self._entries.items()}, f, indent=2)

    def _load(self):
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path) as f:
                content = f.read().strip()
                if not content:
                    return
                data = json.loads(content)
            self._entries = {k: TombstoneEntry.from_dict(v) for k, v in data.items()}
        except Exception:
            self._entries = {}

    def clear(self):
        self._entries = {}
        self._save()
