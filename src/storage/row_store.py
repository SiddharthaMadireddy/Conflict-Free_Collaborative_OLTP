import json, os
from src.core.types import Row

class RowStore:
    def __init__(self, table, snapshot_dir):
        self.table = table
        self.snapshot_path = os.path.join(snapshot_dir, f'{table}.json')
        self._rows = {}
        os.makedirs(snapshot_dir, exist_ok=True)
        self._load()

    def get(self, row_id):
        return self._rows.get(row_id)

    def all_live(self):
        return [r for r in self._rows.values() if not r.deleted]

    def all_including_deleted(self):
        return list(self._rows.values())

    def upsert(self, row, save=True):
        self._rows[row.row_id] = row
        if save:
            self._save()

    def bulk_load(self, rows):
        self._rows = {row.row_id: row for row in rows}
        self._save()

    def tombstone(self, row_id, delete_op_seq):
        row = self._rows.get(row_id)
        if row:
            row.deleted = True
            row.delete_op_seq = delete_op_seq
            self._save()

    def physical_delete(self, row_id):
        self._rows.pop(row_id, None)
        self._save()

    def _save(self):
        with open(self.snapshot_path, 'w') as f:
            json.dump({k: v.to_dict() for k, v in self._rows.items()}, f, indent=2)

    def _load(self):
        if not os.path.exists(self.snapshot_path):
            return
        try:
            with open(self.snapshot_path) as f:
                content = f.read().strip()
                if not content:
                    return
                data = json.loads(content)
            self._rows = {k: Row.from_dict(v) for k, v in data.items()}
        except Exception:
            self._rows = {}

    def clear(self):
        self._rows = {}
        self._save()
