class LWWRegister:
    def __init__(self):
        self._value = None
        self._actor_id = ''
        self._seq = -1

    def set(self, value, actor_id, seq):
        if seq > self._seq or (seq == self._seq and actor_id < self._actor_id):
            self._value = value
            self._actor_id = actor_id
            self._seq = seq

    @property
    def value(self):
        return self._value
