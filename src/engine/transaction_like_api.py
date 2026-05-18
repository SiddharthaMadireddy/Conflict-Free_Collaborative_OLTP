class TransactionLikeAPI:
    def __init__(self, db):
        self.db = db
    def insert(self, table, data):
        self.db.insert(table, data)
    def update(self, table, row_id, data):
        self.db.update(table, row_id, data)
    def delete(self, table, row_id):
        self.db.delete(table, row_id)
