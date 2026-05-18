import shutil
from src.engine.database import Database
from src.replication.replica import Replica
from src.replication.sync_manager import SyncManager

BASE = 'data_test_partition'

def test_partition_merge_keeps_consistency():
    shutil.rmtree(BASE, ignore_errors=True)
    db_a = Database('a', base_dir=BASE, fk_policy='tombstone')
    db_b = Database('b', base_dir=BASE, fk_policy='tombstone')
    db_a.insert('users', {'id':'u1','username':'alice','name':'Alice'})
    SyncManager().sync(Replica('a', BASE), Replica('b', BASE))
    db_a.delete('users', 'u1')
    db_b.insert('posts', {'id':'p1','user_id':'u1','title':'Hello'})
    SyncManager().sync(Replica('a', BASE), Replica('b', BASE))
    posts = Database('a', base_dir=BASE).query('posts')
    assert any(r['id']=='p1' for r in posts)
