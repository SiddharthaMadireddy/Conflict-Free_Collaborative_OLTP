def missing_ops(all_ops, peer_watermark):
    return [op for op in all_ops if op.seq > peer_watermark.get(op.actor_id, 0)]
