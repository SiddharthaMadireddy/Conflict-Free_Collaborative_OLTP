class QueryPlan:
    def __init__(self, table, columns=None, where=None):
        self.table = table
        self.columns = columns
        self.where = where
