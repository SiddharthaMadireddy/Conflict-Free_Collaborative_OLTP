from src.replication.replica import Replica
from src.storage.row_store import RowStore
from src.ops.insert_op import make_insert_op
from src.ops.update_op import make_update_op
from src.ops.delete_op import make_delete_op
from src.query.executor import QueryExecutor
from src.query.materialized_view import MaterializedView
from src.gc.collector import GarbageCollector
from src.engine.bootstrap import load_schemas_and_fks

class Database:
    def __init__(self, replica_id, base_dir='data', fk_policy=None):
        self.replica = Replica(replica_id, base_dir)
        if fk_policy:
            self.replica.metadata.set_fk_policy(fk_policy)
        self.schemas, self.fk_defs = load_schemas_and_fks()
        self._row_stores = {name: RowStore(name, self.replica.snapshots_dir) for name in self.schemas}
        self._rebuild()

    def insert(self, table, data):
        row_id = data.get(self.schemas[table].pk_column)
        op = make_insert_op(self.replica.replica_id, self.replica.next_seq(), table, row_id, data)
        self.replica.op_log.append(op)
        self._rebuild()

    def update(self, table, row_id, data):
        op = make_update_op(self.replica.replica_id, self.replica.next_seq(), table, row_id, data)
        self.replica.op_log.append(op)
        self._rebuild()

    def delete(self, table, row_id):
        seq = self.replica.next_seq()
        op = make_delete_op(self.replica.replica_id, seq, table, row_id)
        self.replica.op_log.append(op)
        self.replica.tombstones.record(table, row_id, self.replica.replica_id, seq)
        self._rebuild()

    def query(self, table, where=None):
        live_rows = {t: [r for r in rows if not r.deleted] for t, rows in self._current_state.items()}
        return QueryExecutor(live_rows).select(table, where=where) if where else QueryExecutor(live_rows).select(table)

    def join_query(self, left, right, left_key, right_key):
        live_rows = {t: [r for r in rows if not r.deleted] for t, rows in self._current_state.items()}
        return QueryExecutor(live_rows).join(left, right, left_key, right_key)

    def gc(self):
        count = GarbageCollector(self.replica).run(self._row_stores)
        self._rebuild()
        return count

    def _rebuild(self):
        self.replica.op_log.compact()
        mv = MaterializedView(self.schemas, self.fk_defs, self.replica.fk_policy)
        self._current_state = mv.build(self.replica.op_log.all_ops())
        for table, rows in self._current_state.items():
            if table not in self._row_stores:
                from src.storage.row_store import RowStore
                self._row_stores[table] = RowStore(table, self.replica.snapshots_dir)
            self._row_stores[table].bulk_load(rows)
