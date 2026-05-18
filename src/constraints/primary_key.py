def resolve_pk_conflicts(rows, schema):
    pk_col = schema.pk_column
    seen = {}
    for row in rows:
        if row.deleted:
            continue
        pk = row.data.get(pk_col)
        if pk is None:
            continue
        if pk not in seen:
            seen[pk] = row
        else:
            winner, loser = seen[pk], row
            if row.row_id < winner.row_id:
                winner, loser = row, winner
            seen[pk] = winner
            loser.deleted = True
    return rows
