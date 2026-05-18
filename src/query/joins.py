def nested_loop_join(left_rows, right_rows, left_key, right_key):
    result = []
    right_index = {}
    for r in right_rows:
        right_index.setdefault(r.data.get(right_key), []).append(r)
    for left in left_rows:
        for right in right_index.get(left.data.get(left_key), []):
            merged = dict(left.data)
            for col, val in right.data.items():
                merged[col if col not in merged else f'right_{col}'] = val
            result.append(merged)
    return result
