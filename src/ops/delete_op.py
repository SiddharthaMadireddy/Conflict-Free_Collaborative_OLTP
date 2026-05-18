from src.ops.operation import Op
from src.core.constants import OP_DELETE
from src.core.utils import now_ms

def make_delete_op(actor_id, seq, table, row_id):
    return Op(OP_DELETE, actor_id, seq, table, row_id, {}, now_ms())
