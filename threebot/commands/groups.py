# Group listing command.

desc = 'Queries available groups.'

def execute(data, argv):
    # query all groups
    c = data.db.conn.cursor()
    c.execute('SELECT * FROM groups ORDER BY groupname')
    rows = c.fetchall()

    pages = data.util.into_pages(['Group', 'Content', 'Author', 'Created'], rows)
    selected = int(argv[0]) - 1 if len(argv) > 0 else 0

    if selected < 0 or selected >= len(pages):
        raise Exception('invalid page number')

    data.reply('Showing page {} of {}'.format(selected + 1, len(pages)))
    data.reply(pages[selected])