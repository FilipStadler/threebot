# Link query command.

desc = 'Retrieves a random link.'

def execute(data, argv):
    # choose a random link
    c = data.db.conn.cursor()
    c.execute('SELECT * FROM links ORDER BY random() LIMIT 1')

    row = c.fetchone()

    if row is None:
        data.reply('No links!')
    else:
        data.bcast('A gift from <a href="{0}">{1}</a>'.format(row[1], row[0]))