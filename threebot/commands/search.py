# Alias listing command.

desc = 'Searches available aliases.'
usage = 'search <KEYWORD> [PAGE]'

def execute(data, argv):
    if len(argv) < 1:
        raise Exception('a keyword is required')

    # Query aliases from the db
    c = data.db.conn.cursor()
    c.execute('SELECT * FROM aliases ORDER BY commandname')
    rows = c.fetchall()

    # Strip command indicators before applying filter
    rows = list(map(lambda obj: [obj[0].removeprefix('!'), obj[1], obj[2], obj[3]], rows))

    # Filter out rows not matching the query
    rows = list(filter(lambda t: t[0].startswith(argv[0]), rows))

    pages = data.util.into_pages(['Alias', 'Action', 'Author', 'Created'], rows)
    page = int(argv[1]) - 1 if len(argv) > 1 else 0

    if page < 0 or page >= len(pages):
        raise Exception('invalid page number')

    data.reply('Showing page {} of {}'.format(page + 1, len(pages)))
    data.reply(pages[page])
