import shutil
from src.engine.database import Database
from src.replication.replica import Replica
from src.replication.sync_manager import SyncManager

BASE = 'data_test_resurrection'

def test_no_resurrection_after_gc_barrier():
    shutil.rmtree(BASE, ignore_errors=True)
    db_a = Database('a', base_dir=BASE, fk_policy='tombstone')
    Database('b', base_dir=BASE, fk_policy='tombstone')
    db_a.insert('users', {'id':'u1','username':'alice','name':'Alice'})
    SyncManager().sync(Replica('a', BASE), Replica('b', BASE))
    db_a.delete('users', 'u1')
    SyncManager().sync(Replica('a', BASE), Replica('b', BASE))
    Database('a', base_dir=BASE).gc()
    rows = Database('a', base_dir=BASE).query('users')
    assert not any(r['id']=='u1' for r in rows)
