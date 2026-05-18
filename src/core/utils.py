import json, os, time, uuid

def now_ms():
    return int(time.time() * 1000)

def new_id():
    try:
        import ulid
        return str(ulid.new())
    except Exception:
        return str(uuid.uuid4())

def load_json_file(path):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)

def save_json_file(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
