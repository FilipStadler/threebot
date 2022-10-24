# Group listing command.

desc = 'Queries available groups.'

def execute(data, argv):
    # query all groups
    c = data.db.conn.cursor()
    c.execute('SELECT * FROM groups ORDER BY groupname')
    rows = c.fetchall()
    headers = ['Group', 'Content', 'Author', 'Created']

    pages = data.util.into_pages(headers, rows)
    selected = int(argv[0]) - 1 if len(argv) > 0 else 0

    if selected < 0 or selected >= len(pages):
        raise Exception('invalid page number')

    data.reply(f'Showing page {selected + 1} of {len(pages)}')
    data.reply(pages[selected])
