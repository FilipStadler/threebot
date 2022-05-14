# Greeting command.

desc = 'Sets or unsets your greeting sound.'
usage = 'greeting [CODE|ALIAS]'

def execute(data, argv):
    c = data.db.conn.cursor()

    if len(argv) > 0:
        # check if username is already in db
        c.execute('SELECT * FROM greetings WHERE username=?', [data.author])

        if len(c.fetchall()) == 0:
            c.execute('INSERT INTO greetings VALUES (?, ?)', [data.author, argv[0]])
        else:
            c.execute('UPDATE greetings SET greeting=? WHERE username=?', [argv[0], data.author])

        data.reply('Set greeting to {0}.'.format(argv[0]))
    else:
        c.execute('DELETE FROM greetings WHERE username=?', [data.author])
        data.reply('Removed greeting.')

    data.db.conn.commit()
