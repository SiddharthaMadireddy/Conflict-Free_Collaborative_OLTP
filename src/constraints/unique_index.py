def resolve_unique_conflicts(rows, schema):
    for col in schema.unique_columns:
        seen = {}
        for row in rows:
            if row.deleted:
                continue
            val = row.data.get(col)
            if val is None:
                continue
            if val not in seen:
                seen[val] = row
            else:
                winner, loser = seen[val], row
                if row.row_id < winner.row_id:
                    winner, loser = row, winner
                seen[val] = winner
                loser.data[col] = f"{val}#conflict#{loser.row_id}"

    for cols in getattr(schema, 'composite_unique', []):
        seen = {}
        for row in rows:
            if row.deleted: continue
            key = tuple(row.data.get(c) for c in cols)
            if any(v is None for v in key): continue
            if key not in seen:
                seen[key] = row
            else:
                winner, loser = seen[key], row
                if row.row_id < winner.row_id:
                    winner, loser = row, winner
                seen[key] = winner
                last_col = cols[-1]
                loser.data[last_col] = f"{loser.data[last_col]}#conflict#{loser.row_id}"

    return rows

