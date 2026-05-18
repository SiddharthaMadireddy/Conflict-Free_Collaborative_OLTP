from src.ops.operation import Op

class SyncMessage:
    def __init__(self, sender_id, ops, watermark):
        self.sender_id = sender_id
        self.ops = ops
        self.watermark = watermark

    def to_dict(self):
        return {'sender_id': self.sender_id, 'ops': [o.to_dict() for o in self.ops], 'watermark': self.watermark}

    @classmethod
    def from_dict(cls, d):
        return cls(d['sender_id'], [Op.from_dict(x) for x in d['ops']], d['watermark'])
