# Sound query command.

desc = 'Lists available sounds.'
usage = 'sounds [PAGENUM]'

def execute(data, argv):
    # query all sounds
    c = data.db.conn.cursor()
    c.execute('SELECT * FROM sounds ORDER BY created')
    rows = c.fetchall()

    pages = data.util.into_pages(['Sound', 'Author', 'Created'], rows)
    selected = int(argv[0]) - 1 if len(argv) > 0 else 0

    if selected < 0 or selected >= len(pages):
        raise Exception('invalid page number')

    data.reply('Showing page {} of {}'.format(selected + 1, len(pages)))
    data.reply(pages[selected])