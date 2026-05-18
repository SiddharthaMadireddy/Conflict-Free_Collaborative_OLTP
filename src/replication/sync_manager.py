class SyncManager:
    def sync(self, replica_a, replica_b):
        self._one_way(replica_a, replica_b)
        self._one_way(replica_b, replica_a)
        replica_a.metadata.merge_watermarks(replica_b.watermark())
        replica_b.metadata.merge_watermarks(replica_a.watermark())
        replica_a.peer_state.update_peer_watermark(replica_b.replica_id, replica_b.watermark())
        replica_b.peer_state.update_peer_watermark(replica_a.replica_id, replica_a.watermark())

    def _one_way(self, sender, receiver):
        missing = sender.op_log.ops_not_seen_by(receiver.op_log.watermark())
        for op in missing:
            receiver.op_log.append(op)
