from src.crdt.merge import merge_ops_to_rows
from src.ops.insert_op import make_insert_op
from src.ops.delete_op import make_delete_op
from src.ops.update_op import make_update_op

def test_insert_merge():
    rows = merge_ops_to_rows([make_insert_op('a',1,'users','u1',{'id':'u1','name':'Alice'})])
    assert rows['u1'].data['name'] == 'Alice'
    assert not rows['u1'].deleted

def test_delete_tombstones_row():
    rows = merge_ops_to_rows([
        make_insert_op('a',1,'users','u1',{'id':'u1','name':'Alice'}),
        make_delete_op('a',2,'users','u1')
    ])
    assert rows['u1'].deleted

def test_concurrent_update_lww():
    rows = merge_ops_to_rows([
        make_insert_op('a',1,'users','u1',{'id':'u1','name':'Alice'}),
        make_update_op('a',2,'users','u1',{'name':'Alice Updated'}),
        make_update_op('b',3,'users','u1',{'name':'Bob Override'})
    ])
    assert rows['u1'].data['name'] == 'Bob Override'
