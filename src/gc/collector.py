from src.gc.tombstone_gc import TombstoneGC

class GarbageCollector:
    def __init__(self, replica):
        self.replica = replica
        self._gc = TombstoneGC()

    def run(self, row_stores):
        all_watermarks = {self.replica.replica_id: self.replica.watermark()}
        for peer_id in ['a', 'b']:
            if peer_id != self.replica.replica_id:
                all_watermarks[peer_id] = self.replica.peer_state.get_peer_watermark(peer_id)
        return self._gc.run(self.replica.tombstones, row_stores, all_watermarks)
