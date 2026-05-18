from adapters.myteam import Engine
import json

engine = Engine()
engine.open_peer('A', fk_policy='tombstone')
engine.open_peer('B', fk_policy='tombstone')
engine.open_peer('C', fk_policy='tombstone')

stmts = [
    """CREATE TABLE users (
      id    TEXT PRIMARY KEY,
      email TEXT NOT NULL UNIQUE,
      name  TEXT
    );""",
    """CREATE TABLE orders (
      id          TEXT PRIMARY KEY,
      user_id     TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
      status      TEXT NOT NULL,
      total_cents INTEGER NOT NULL DEFAULT 0
    );"""
]

for peer in ['A', 'B', 'C']:
    engine.apply_schema(peer, stmts)

engine.execute('A', "INSERT INTO users (id, email, name) VALUES ('u1', 'alice@x.com', 'Alice')")
engine.execute('A', "INSERT INTO users (id, email, name) VALUES ('u2', 'bob@x.com', 'Bob')")
engine.execute('B', "INSERT INTO users (id, email, name) VALUES ('u3', 'alice@x.com', 'AlicePrime')")

# Sync A to C
engine.sync('A', 'C')

engine.execute('C', "DELETE FROM users WHERE id='u1'")

engine.execute('A', "INSERT INTO orders (id, user_id, status, total_cents) VALUES ('o1', 'u1', 'pending', '1200')")
engine.execute('A', "UPDATE users SET name='Alice Cooper' WHERE id='u1'")

engine.execute('B', "UPDATE users SET email='alice@ex.org' WHERE id='u1'")

engine.sync('A', 'B')
engine.sync('B', 'C')
engine.sync('A', 'C')
# Sync until quiescent
engine.sync('A', 'B')

for peer in ['A', 'B', 'C']:
    print(peer, engine.snapshot_hash(peer))

print("State A:")
print(json.dumps(engine.snapshot_state('A'), indent=2))
