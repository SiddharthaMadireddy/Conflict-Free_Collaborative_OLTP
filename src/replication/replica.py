import os
from src.storage.op_log import OpLog
from src.storage.tombstone_store import TombstoneStore
from src.storage.metadata_store import MetadataStore
from src.replication.peer_state import PeerState

class Replica:
    def __init__(self, replica_id, base_dir='data'):
        self.replica_id = replica_id
        safe_id = replica_id.replace(':', '_')
        self.replica_dir = os.path.join(base_dir, f'replica_{safe_id}')
        self.op_log = OpLog(os.path.join(self.replica_dir, 'oplog', 'ops.jsonl'))
        self.tombstones = TombstoneStore(self.replica_dir)
        self.metadata = MetadataStore(self.replica_dir)
        self.peer_state = PeerState(self.replica_dir)
        self.snapshots_dir = os.path.join(self.replica_dir, 'snapshots')
        os.makedirs(self.snapshots_dir, exist_ok=True)

    @property
    def fk_policy(self):
        return self.metadata.get_fk_policy()

    def next_seq(self):
        return self.op_log.next_seq(self.replica_id)

    def watermark(self):
        return self.op_log.watermark()
