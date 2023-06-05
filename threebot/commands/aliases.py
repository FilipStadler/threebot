# Alias listing command.

desc = 'Lists available aliases.'
usage = 'aliases [PAGENUM]'

def execute(data, argv):
    # query all aliases
    c = data.db.conn.cursor()
    c.execute('SELECT * FROM aliases ORDER BY commandname')
    rows = c.fetchall()

    if len(rows) == 0:
        data.reply('No aliases found.')
        return

    pages = data.util.into_pages(['Alias', 'Action', 'Author', 'Created'], rows)

    selected = int(argv[0]) - 1 if len(argv) > 0 else 0

    if selected < 0 or selected >= len(pages):
        raise Exception(f'invalid page number {selected}, must be between 1 and {len(pages)}')

    data.reply('Showing page {} of {}'.format(selected + 1, len(pages)))
    data.reply(pages[selected])
