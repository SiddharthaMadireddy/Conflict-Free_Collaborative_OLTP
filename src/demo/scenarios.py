from src.engine.database import Database
from src.replication.replica import Replica
from src.replication.sync_manager import SyncManager

def run_partition_sync_demo():
    for rid in ['a', 'b']:
        db = Database(rid, fk_policy='tombstone')
        db.replica.op_log.clear()
        db.replica.tombstones.clear()
        db.replica.metadata.clear()
        db.replica.metadata.set_fk_policy('tombstone')
        db._rebuild()
    db_a = Database('a', fk_policy='tombstone')
    db_a.insert('users', {'id':'u1','username':'alice','name':'Alice'})
    SyncManager().sync(Replica('a'), Replica('b'))
    Database('b', fk_policy='tombstone')
    db_a = Database('a', fk_policy='tombstone')
    db_b = Database('b', fk_policy='tombstone')
    db_a.delete('users', 'u1')
    db_b.insert('posts', {'id':'p1','user_id':'u1','title':'Hello World','body':'My first post'})
    SyncManager().sync(Replica('a'), Replica('b'))
    print('Users on A:', Database('a').query('users'))
    print('Posts on A:', Database('a').query('posts'))

if __name__ == '__main__':
    run_partition_sync_demo()
