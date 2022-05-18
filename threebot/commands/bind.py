# Custom bind command.

desc = 'Plays your bind sound. Rebinds on input.'
usage = 'bind [CODE|ALIAS]'

def execute(data, argv):
    # search for user bind
    c = data.db.conn.cursor()
    c.execute('SELECT bind FROM binds WHERE username=?', [data.author])

    results = c.fetchone()
 
    if len(argv) < 1:
        data.util.play_sound_or_alias(results[0])
        data.reply('Playing bind: {}'.format(results[0]))
        return

    if len(argv) > 1:
        raise Exception('too many arguments. Usage: bind [CODE|ALIAS]')

    # check if binding or rebinding
    c.execute('SELECT * FROM binds WHERE username=?', [data.author])
    results = c.fetchone()
    if results is None:
        c.execute('INSERT INTO binds VALUES (?, ?)', [data.author, argv[0]])
    else:
        c.execute('UPDATE binds SET bind=? WHERE username=?', [argv[0], data.author])

    data.db.conn.commit()
    data.reply('Set bind to {0}.'.format(argv[0]))
