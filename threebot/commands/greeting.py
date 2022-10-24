# Greeting command.

desc = 'Sets or unsets your greeting sound.'
usage = 'greeting [CODE|ALIAS]'

def execute(data, argv):
    c = data.db.conn.cursor()

    c.execute('SELECT * FROM greetings WHERE username=?', [data.author])
    res = c.fetchall()

    if len(argv) > 0:
        # check if username is already in db
        c.execute('SELECT * FROM greetings WHERE username=?', [data.author])

        if len(res) == 0:
            param = (data.author, argv[0])
            c.execute('INSERT INTO greetings VALUES (?, ?)', param)
        else:
            param = (argv[0], data.author)
            c.execute('UPDATE greetings SET greeting=? WHERE username=?', param)

        data.reply('Set greeting to {0}.'.format(argv[0]))
    else:
        if len(res) > 0:
            c.execute('DELETE FROM greetings WHERE username=?', [data.author])
            data.reply(f'Removed greeting (previous greeting was {res[0]})')
        else:
            data.reply('Greeting is not set! Set it with "!greeting SOUND".')

    data.db.conn.commit()
