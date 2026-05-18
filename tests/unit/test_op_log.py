from src.storage.op_log import OpLog
from src.ops.insert_op import make_insert_op
import tempfile, os

def test_append_and_read():
    with tempfile.TemporaryDirectory() as td:
        log = OpLog(os.path.join(td, 'ops.jsonl'))
        log.append(make_insert_op('a',1,'users','u1',{'id':'u1'}))
        ops = log.all_ops()
        assert len(ops) == 1
        assert ops[0].row_id == 'u1'
