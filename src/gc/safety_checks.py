def is_tombstone_safe(delete_actor, delete_seq, all_replica_watermarks):
    for _, watermark in all_replica_watermarks.items():
        if watermark.get(delete_actor, 0) < delete_seq:
            return False
    return True
