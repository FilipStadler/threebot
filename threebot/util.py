# Generic utilities for use by all commands.

def into_pages(headers, rows, rows_per_page=32):
    pages = []

    while len(rows) > 0:
        msg = '<table><tr>'
        
        for h in headers:
            msg += '<th>{0}</th>'.format(h)

        msg += '</tr>'

        for r in rows[0:rows_per_page]:
            msg += '<tr>'

            for el in r:
                msg += '<td>{0}</td>'.format(el)

        msg += '</table>'
        pages.append(msg)

        rows = rows[rows_per_page:]

    return pages