import shutil
from src.engine.database import Database
from src.replication.replica import Replica
from src.replication.sync_manager import SyncManager

BASE = 'data_test_fk'

def test_fk_conflict_tombstone():
    shutil.rmtree(BASE, ignore_errors=True)
    db_a = Database('a', base_dir=BASE, fk_policy='tombstone')
    Database('b', base_dir=BASE, fk_policy='tombstone')
    db_a.insert('users', {'id':'u1','username':'alice','name':'Alice'})
    SyncManager().sync(Replica('a', BASE), Replica('b', BASE))
    db_a.delete('users', 'u1')
    Database('b', base_dir=BASE, fk_policy='tombstone').insert('posts', {'id':'p1','user_id':'u1','title':'Hello'})
    SyncManager().sync(Replica('a', BASE), Replica('b', BASE))
    db = Database('a', base_dir=BASE, fk_policy='tombstone')
    assert any(r['id']=='p1' for r in db.query('posts'))
    assert not any(r['id']=='u1' for r in db.query('users'))
