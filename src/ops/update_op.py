from src.ops.operation import Op
from src.core.constants import OP_UPDATE
from src.core.utils import now_ms

def make_update_op(actor_id, seq, table, row_id, data):
    return Op(OP_UPDATE, actor_id, seq, table, row_id, data, now_ms())
