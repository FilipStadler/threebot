# Rebind command.

desc = 'Assigns your bind sound for \'!bind\'.'
usage = 'rebind [CODE|ALIAS]'

def execute(data, argv):
    c = data.db.conn.cursor()

    if len(argv) < 1:
        raise Exception('expected argument')

    # check if binding or rebinding
    c.execute('SELECT * FROM binds WHERE username=?', [data.author])

    results = c.fetchone()

    if results is None:
        c.execute('INSERT INTO binds VALUES (?, ?)', [data.author, argv[0]])
    else:
        c.execute('UPDATE binds SET name=? WHERE username=?', [argv[0], data.author])

    data.db.conn.commit()
    data.reply('Set bind to {0}.'.format(argv[0]))
