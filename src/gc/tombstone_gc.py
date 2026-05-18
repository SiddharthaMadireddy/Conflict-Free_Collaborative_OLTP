from src.gc.safety_checks import is_tombstone_safe

class TombstoneGC:
    def run(self, tombstone_store, row_stores, all_watermarks):
        collected = 0
        for entry in list(tombstone_store.all_entries()):
            if is_tombstone_safe(entry.actor_id, entry.seq, all_watermarks):
                store = row_stores.get(entry.table)
                if store:
                    store.physical_delete(entry.row_id)
                tombstone_store.remove(entry.table, entry.row_id)
                collected += 1
        return collected
