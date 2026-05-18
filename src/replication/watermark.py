class Watermark:
    def __init__(self, data=None):
        self._wm = dict(data or {})
    def update(self, actor_id, seq):
        self._wm[actor_id] = max(self._wm.get(actor_id, 0), seq)
    def merge(self, other):
        for actor_id, seq in other.items():
            self.update(actor_id, seq)
    def to_dict(self):
        return dict(self._wm)
