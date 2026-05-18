try:
    from tabulate import tabulate
except ModuleNotFoundError:
    tabulate = None

def print_table(rows, empty_message='No rows.'):
    if rows:
        if tabulate:
            print(tabulate(rows, headers='keys', tablefmt='rounded_outline'))
        else:
            # Fallback table printer if tabulate is not installed
            headers = list(rows[0].keys())
            col_widths = {h: max(len(str(h)), max(len(str(r.get(h, ''))) for r in rows)) for h in headers}
            header_line = " | ".join(f"{str(h):<{col_widths[h]}}" for h in headers)
            separator = "-+-".join("-" * col_widths[h] for h in headers)
            print(header_line)
            print(separator)
            for r in rows:
                print(" | ".join(f"{str(r.get(h, '')):<{col_widths[h]}}" for h in headers))
    else:
        print(empty_message)
