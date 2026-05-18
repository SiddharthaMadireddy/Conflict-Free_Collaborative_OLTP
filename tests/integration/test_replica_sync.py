import shutil
from src.engine.database import Database
from src.replication.replica import Replica
from src.replication.sync_manager import SyncManager

BASE = 'data_test_sync'

def test_basic_sync():
    shutil.rmtree(BASE, ignore_errors=True)
    db_a = Database('a', base_dir=BASE, fk_policy='tombstone')
    Database('b', base_dir=BASE, fk_policy='tombstone')
    db_a.insert('users', {'id':'u1','username':'alice','name':'Alice'})
    SyncManager().sync(Replica('a', BASE), Replica('b', BASE))
    rows = Database('b', base_dir=BASE).query('users')
    assert any(r['id']=='u1' for r in rows)
