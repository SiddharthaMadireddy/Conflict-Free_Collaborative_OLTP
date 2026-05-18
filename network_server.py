import click
import json
import requests
from flask import Flask, request, jsonify
from src.replication.replica import Replica
from src.ops.operation import Op
from src.engine.database import Database

app = Flask(__name__)
REPLICA = None

@app.route('/', methods=['GET'])
def index():
    """Root route to check server status."""
    if REPLICA:
        return jsonify({
            "status": "CRDT Relational Engine Replica Running",
            "replica_id": REPLICA.replica_id,
            "watermark": REPLICA.watermark()
        })
    return jsonify({"status": "Initializing..."})

@app.route('/watermark', methods=['GET'])
def get_watermark():
    """Return the current watermark of this replica."""
    return jsonify({
        "replica_id": REPLICA.replica_id,
        "watermark": REPLICA.watermark()
    })

@app.route('/ops', methods=['POST'])
def receive_ops():
    """Receive operations from a remote peer."""
    data = request.json
    remote_replica_id = data['replica_id']
    remote_watermark = data['watermark']
    ops = [Op.from_dict(o) for o in data['ops']]
    
    for op in ops:
        REPLICA.op_log.append(op)
        
    REPLICA.metadata.merge_watermarks(remote_watermark)
    REPLICA.peer_state.update_peer_watermark(remote_replica_id, remote_watermark)
    
    # Re-instantiate database to update in-memory state if needed, though OpLog is source of truth.
    Database(REPLICA.replica_id)
    return jsonify({"status": "ok", "appended": len(ops)})

@app.route('/ops_not_seen', methods=['POST'])
def get_ops_not_seen():
    """Return operations this replica has that the remote hasn't seen."""
    remote_watermark = request.json.get('watermark', {})
    missing_ops = REPLICA.op_log.ops_not_seen_by(remote_watermark)
    return jsonify({"ops": [op.to_dict() for op in missing_ops]})

@click.group()
def cli():
    pass

@cli.command()
@click.option('--replica', required=True, help="Replica ID (e.g. A or B)")
@click.option('--port', default=5000, help="Port to run the server on")
def serve(replica, port):
    """Run the HTTP server for a peer."""
    global REPLICA
    REPLICA = Replica(replica)
    # Ensure database is initialized
    Database(replica)
    print(f"Starting server for Replica '{replica}' on port {port}...")
    app.run(host='0.0.0.0', port=port)

@cli.command()
@click.option('--replica', required=True, help="Local Replica ID")
@click.option('--target', required=True, help="Target peer URL (e.g. http://192.168.1.5:5000)")
def sync(replica, target):
    """Sync local replica with a remote peer."""
    global REPLICA
    REPLICA = Replica(replica)
    
    print(f"Syncing local replica '{replica}' with remote '{target}'...")
    
    try:
        # 1. Get remote watermark
        resp = requests.get(f"{target}/watermark")
        resp.raise_for_status()
        remote_info = resp.json()
        remote_replica_id = remote_info['replica_id']
        remote_wm = remote_info['watermark']
        
        # 2. Send our missing ops to remote
        missing_for_remote = REPLICA.op_log.ops_not_seen_by(remote_wm)
        if missing_for_remote:
            requests.post(f"{target}/ops", json={
                "replica_id": REPLICA.replica_id,
                "watermark": REPLICA.watermark(),
                "ops": [o.to_dict() for o in missing_for_remote]
            })
            print(f"Sent {len(missing_for_remote)} operations to {remote_replica_id}")
        else:
            print(f"No new operations to send to {remote_replica_id}")
            
        # 3. Get remote ops that we are missing
        resp = requests.post(f"{target}/ops_not_seen", json={
            "watermark": REPLICA.watermark()
        })
        resp.raise_for_status()
        remote_ops_data = resp.json()['ops']
        remote_ops = [Op.from_dict(o) for o in remote_ops_data]
        
        for op in remote_ops:
            REPLICA.op_log.append(op)
            
        if remote_ops:
            print(f"Received {len(remote_ops)} operations from {remote_replica_id}")
        else:
            print(f"No new operations received from {remote_replica_id}")
            
        # 4. Update local metadata
        REPLICA.metadata.merge_watermarks(remote_wm)
        REPLICA.peer_state.update_peer_watermark(remote_replica_id, remote_wm)
        
        # Refresh the database view
        Database(replica)
        print("Sync completed successfully.")
        
    except Exception as e:
        print(f"Sync failed: {e}")

if __name__ == '__main__':
    cli()
