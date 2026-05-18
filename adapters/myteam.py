import re
import hashlib
import json
import shutil
import os
from adapter import Adapter
from src.engine.database import Database
from src.schema.table_schema import TableSchema
from src.schema.column_schema import ColumnSchema
from src.schema.fk_schema import FKSchema

class MyEngine:
    def __init__(self, peer_id, fk_policy):
        safe_peer_id = peer_id.replace(':', '_')
        dir_name = f"data_{safe_peer_id}"
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
            except Exception:
                pass
        self.db = Database(peer_id, base_dir=dir_name, fk_policy=fk_policy)
        self.db.schemas = {}
        self.db.fk_defs = []

    def execute(self, sql, params=()):
        sql_upper = sql.upper().strip()
        if sql_upper.startswith("CREATE TABLE"):
            self._parse_create_table(sql)
        elif sql_upper.startswith("CREATE INDEX"):
            pass  # Ignored for now
        elif sql_upper.startswith("INSERT"):
            self._parse_insert(sql, params)
        elif sql_upper.startswith("UPDATE"):
            self._parse_update(sql, params)
        elif sql_upper.startswith("DELETE"):
            self._parse_delete(sql, params)
        else:
            raise ValueError(f"Unknown SQL: {sql}")

    def _parse_create_table(self, sql):
        # Extremely basic parser for the specific schemas
        match = re.search(r'CREATE\s+TABLE\s+(\w+)\s*\((.*)\)', sql, re.IGNORECASE | re.DOTALL)
        if not match:
            return
        table_name = match.group(1).lower()
        content = match.group(2)
        
        composite_unique = []
        for m in re.finditer(r'UNIQUE\s*\(([^)]+)\)', content, re.IGNORECASE):
            u_cols = [c.strip().lower() for c in m.group(1).split(',')]
            composite_unique.append(u_cols)
        content = re.sub(r'UNIQUE\s*\([^)]+\)', '', content, flags=re.IGNORECASE)
        
        cols_def = content.split(',')
        
        columns = []
        for cdef in cols_def:
            cdef = cdef.strip()
            if not cdef: continue
            
            parts = cdef.split()
            cname = parts[0].lower()
            ctype = parts[1].lower()
            is_pk = 'PRIMARY KEY' in cdef.upper()
            is_unique = 'UNIQUE' in cdef.upper()
            columns.append(ColumnSchema(cname, ctype, primary_key=is_pk, unique=is_unique))
            
            if 'REFERENCES' in cdef.upper():
                ref_match = re.search(r'REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)', cdef, re.IGNORECASE)
                if ref_match:
                    parent_table = ref_match.group(1).lower()
                    parent_col = ref_match.group(2).lower()
                    self.db.fk_defs.append(FKSchema(table_name, cname, parent_table, parent_col))
                    
        self.db.schemas[table_name] = TableSchema(table_name, columns, composite_unique=composite_unique)
        if table_name not in self.db._row_stores:
            from src.storage.row_store import RowStore
            self.db._row_stores[table_name] = RowStore(table_name, self.db.replica.snapshots_dir)

    def _parse_insert(self, sql, params):
        match = re.search(r'INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)', sql, re.IGNORECASE)
        if not match:
            # Fallback for "INSERT table (cols) VALUES (vals)" or similar
            match = re.search(r'INSERT\s+(\w+)\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)', sql, re.IGNORECASE)
            if not match:
                # Fallback for trace notation from prompt: INSERT users (u1, alice@x.com, "Alice")
                match = re.search(r'INSERT\s+(\w+)\s*\(([^)]+)\)', sql, re.IGNORECASE)
                if match:
                    table = match.group(1).lower()
                    vals = [v.strip().strip("'\"") for v in match.group(2).split(',')]
                    schema = self.db.schemas[table]
                    data = dict(zip([c.name for c in schema.columns], vals))
                    self.db.insert(table, data)
                return

        table = match.group(1).lower()
        cols = [c.strip() for c in match.group(2).split(',')]
        if params:
            vals = params
        else:
            vals = [v.strip().strip("'\"") for v in match.group(3).split(',')]
        data = dict(zip(cols, vals))
        self.db.insert(table, data)

    def _parse_update(self, sql, params):
        match = re.search(r'UPDATE\s+(\w+)\s+SET\s+(.+?)\s+WHERE\s+(.+)', sql, re.IGNORECASE)
        if not match: return
        table = match.group(1).lower()
        set_clause = match.group(2)
        where_clause = match.group(3)
        
        data = {}
        param_idx = 0
        # Parse set assignments
        for assignment in set_clause.split(','):
            c, v = assignment.split('=')
            c = c.strip()
            v = v.strip()
            if v == '?':
                v = params[param_idx]
                param_idx += 1
            else:
                v = v.strip("'\"")
            data[c] = v
            
        # Parse where
        id_col, id_val = where_clause.split('=')
        id_val = id_val.strip()
        if id_val == '?':
            id_val = params[param_idx]
            param_idx += 1
        else:
            id_val = id_val.strip("'\"")
        
        self.db.update(table, id_val, data)

    def _parse_delete(self, sql, params):
        match = re.search(r'DELETE\s+FROM\s+(\w+)\s+WHERE\s+(.+)', sql, re.IGNORECASE)
        if not match:
            match = re.search(r'DELETE\s+(\w+)\s+WHERE\s+(.+)', sql, re.IGNORECASE)
        if not match: return
        table = match.group(1).lower()
        where_clause = match.group(2)
        id_col, id_val = where_clause.split('=')
        id_val = id_val.strip()
        if id_val == '?':
            id_val = params[0]
        else:
            id_val = id_val.strip("'\"")
        self.db.delete(table, id_val)

    def sync_with(self, other):
        # Get operations from other that we don't have
        my_ops = self.db.replica.op_log.all_ops()
        other_ops = other.db.replica.op_log.all_ops()
        
        my_op_ids = {op.op_id for op in my_ops}
        other_op_ids = {op.op_id for op in other_ops}
        
        my_new = [op for op in other_ops if op.op_id not in my_op_ids]
        other_new = [op for op in my_ops if op.op_id not in other_op_ids]
        
        self.db.replica.op_log.bulk_append(my_new)
        other.db.replica.op_log.bulk_append(other_new)
                
        self.db.replica.op_log.compact()
        other.db.replica.op_log.compact()
                
        self.db._rebuild()
        other.db._rebuild()

    def state_hash(self):
        state = self.dump_tables()
        for t in state:
            state[t].sort(key=lambda d: str(sorted(d.items())))
        hasher = hashlib.sha256()
        hasher.update(json.dumps(state, sort_keys=True).encode())
        return hasher.hexdigest()

    def dump_tables(self):
        state = {}
        for table, rows in self.db._current_state.items():
            state[table] = []
            for row in rows:
                if not row.deleted:
                    state[table].append(row.data)
        return state

    def shutdown(self):
        pass


class Engine(Adapter):
    def __init__(self):
        self.peers = {}

    def open_peer(self, peer_id, fk_policy=None):
        self.peers[peer_id] = MyEngine(peer_id, fk_policy=fk_policy)

    def apply_schema(self, peer_id, stmts):
        for s in stmts:
            self.peers[peer_id].execute(s)

    def execute(self, peer_id, sql, params=()):
        self.peers[peer_id].execute(sql, params)

    def sync(self, peer_a, peer_b):
        self.peers[peer_a].sync_with(self.peers[peer_b])

    def snapshot_hash(self, peer_id):
        return self.peers[peer_id].state_hash()

    def snapshot_state(self, peer_id):
        return self.peers[peer_id].dump_tables()

    def close(self):
        for p in self.peers.values():
            p.shutdown()
