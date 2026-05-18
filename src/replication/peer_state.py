import json, os

class PeerState:
    def __init__(self, replica_dir):
        self.path = os.path.join(replica_dir, 'peer_state.json')
        self._state = {}
        os.makedirs(replica_dir, exist_ok=True)
        self._load()

    def get_peer_watermark(self, peer_id):
        return dict(self._state.get(peer_id, {}))

    def update_peer_watermark(self, peer_id, watermark):
        current = self._state.get(peer_id, {})
        for actor, seq in watermark.items():
            current[actor] = max(current.get(actor, 0), seq)
        self._state[peer_id] = current
        self._save()

    def _save(self):
        with open(self.path, 'w') as f:
            json.dump(self._state, f, indent=2)

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path) as f:
                    content = f.read().strip()
                    if content:
                        self._state = json.loads(content)
            except Exception:
                pass
