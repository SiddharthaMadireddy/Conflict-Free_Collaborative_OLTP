def all_rows(_):
    return True

def eq(column, value):
    return lambda row: row.data.get(column) == value
