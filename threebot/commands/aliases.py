# Alias listing command.

desc = 'Lists available aliases.'
usage = 'aliases [PAGENUM]'

def execute(data, argv):
    # query all aliases
    c = data.db.conn.cursor()
    c.execute('SELECT * FROM aliases ORDER BY commandname')
    rows = c.fetchall()

    pages = data.util.into_pages(['Alias', 'Action', 'Author', 'Created'], rows)
    selected = int(argv[0]) - 1 if len(argv) > 0 else 0

    if selected < 0 or selected >= len(pages):
        raise Exception('invalid page number')

    data.reply('Showing page {} of {}'.format(selected + 1, len(pages)))
    data.reply(pages[selected])
