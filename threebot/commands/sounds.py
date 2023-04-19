# Sound query command.

desc = 'Lists available sounds.'
usage = 'sounds [PAGENUM]'

def execute(data, argv):
    # query all sounds
    c = data.db.conn.cursor()
    c.execute('SELECT * FROM sounds ORDER BY timestamp DESC')
    rows = c.fetchall()
    headers = ['Sound', 'Author', 'Created', 'Source', 'Start', 'Length']

    new_rows = []

    for row in rows:
        # Search the db for matching aliases
        c.execute(f'SELECT * FROM aliases WHERE action LIKE "!s%{row[0]}"')
        aliases = c.fetchall()
        new_rows.append(row + (' '.join([a[0] for a in aliases]),))

    pages = data.util.into_pages(['Sound', 'Author', 'Created', 'Source', 'Start', 'Length', 'Aliases'], new_rows)
    selected = int(argv[0]) - 1 if len(argv) > 0 else 0

    if selected < 0 or selected >= len(pages):
        raise Exception('invalid page number')

    data.reply('Showing page {} of {}'.format(selected + 1, len(pages)))
    data.reply(pages[selected])
