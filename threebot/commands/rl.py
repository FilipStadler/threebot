# Link query command.

desc = 'Retrieves a random link.'
usage = 'rl [username]'

def execute(data, argv):
    if len(argv) == 0:
        # choose a random link
        c = data.db.conn.cursor()
        c.execute('SELECT * FROM links ORDER BY random() LIMIT 1')
    elif len(argv) == 1:
        # choose a random link from a specific user
        c = data.db.conn.cursor()
        c.execute('SELECT * FROM links WHERE username=? ORDER BY random() LIMIT 1', [argv[0]])
    else:
        raise Exception('Usage: ' + usage)

    row = c.fetchone()

    if row is None:
        data.reply('No links!')
    else:
        data.bcast('A gift from <a href="{0}">{1}</a>'.format(row[1], row[0]))