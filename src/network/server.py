import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import asyncio
from src.replication.replica import Replica
from src.ops.operation import Op

class CRDTHttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/watermark':
            query = urllib.parse.parse_qs(parsed.query)
            replica_id = query.get('replica', ['a'])[0]
            rep = Replica(replica_id)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(rep.watermark()).encode())
        elif parsed.path == '/ops':
            query = urllib.parse.parse_qs(parsed.query)
            replica_id = query.get('replica', ['a'])[0]
            wm_str = query.get('wm', ['{}'])[0]
            wm = json.loads(wm_str)
            rep = Replica(replica_id)
            missing = rep.op_log.ops_not_seen_by(wm)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps([op.to_dict() for op in missing]).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/ops':
            query = urllib.parse.parse_qs(parsed.query)
            replica_id = query.get('replica', ['a'])[0]
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            ops_data = json.loads(body.decode())
            rep = Replica(replica_id)
            wm = rep.watermark()
            
            for op_dict in ops_data:
                op = Op.from_dict(op_dict)
                if op.seq > wm.get(op.actor_id, 0):
                    rep.op_log.append(op)
                    
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress verbose logging to keep CLI clean
        pass


class Server:
    def __init__(self, host='0.0.0.0', port=8000):
        self.host = host
        self.port = port
        self.server = None

    def _run(self):
        self.server = HTTPServer((self.host, self.port), CRDTHttpHandler)
        print(f"[Network] CRDT Sync Server listening on http://{self.host}:{self.port}")
        self.server.serve_forever()

    async def start(self):
        import threading
        t = threading.Thread(target=self._run, daemon=True)
        t.start()

