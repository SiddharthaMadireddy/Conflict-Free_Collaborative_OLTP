import json
import urllib.request
import urllib.parse
from src.replication.replica import Replica
from src.ops.operation import Op

class NetworkClient:
    def __init__(self, remote_url):
        self.remote_url = remote_url.rstrip('/')

    def sync(self, local_replica_id, remote_replica_id):
        local_rep = Replica(local_replica_id)
        
        # 1. Get remote watermark
        req = urllib.request.Request(f"{self.remote_url}/watermark?replica={remote_replica_id}")
        with urllib.request.urlopen(req) as resp:
            remote_wm = json.loads(resp.read().decode())
            
        # 2. Send local ops missing from remote
        local_missing = local_rep.op_log.ops_not_seen_by(remote_wm)
        if local_missing:
            data = json.dumps([op.to_dict() for op in local_missing]).encode()
            post_req = urllib.request.Request(
                f"{self.remote_url}/ops?replica={remote_replica_id}",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(post_req) as resp:
                resp.read() # Consume response
                
        # 3. Fetch remote ops missing from local
        local_wm_str = urllib.parse.quote(json.dumps(local_rep.watermark()))
        get_req = urllib.request.Request(f"{self.remote_url}/ops?replica={remote_replica_id}&wm={local_wm_str}")
        with urllib.request.urlopen(get_req) as resp:
            remote_ops_data = json.loads(resp.read().decode())
            
        # 4. Append remote ops to local log
        local_wm = local_rep.watermark()
        for op_dict in remote_ops_data:
            op = Op.from_dict(op_dict)
            if op.seq > local_wm.get(op.actor_id, 0):
                local_rep.op_log.append(op)
                
        # 5. Merge watermarks
        local_rep.metadata.merge_watermarks(remote_wm)
        local_rep.peer_state.update_peer_watermark(remote_replica_id, remote_wm)
