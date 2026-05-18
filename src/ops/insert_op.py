from src.ops.operation import Op
from src.core.constants import OP_INSERT
from src.core.utils import now_ms

def make_insert_op(actor_id, seq, table, row_id, data):
    return Op(OP_INSERT, actor_id, seq, table, row_id, data, now_ms())
