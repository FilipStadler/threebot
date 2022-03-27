# Sound information query.

desc = "Queries information about a sound."
usage = "sinfo [CODE/ALIAS]"

def execute(data, argv):
    if len(argv) < 1:
        raise Exception('expected argument')

    target = data.db.resolve_alias(argv[0]) or argv[0]

    c = data.db.conn.cursor()
    c.execute('SELECT * FROM sounds WHERE soundname=?', [target])

    res = c.fetchone()

    if not res:
        raise Exception('{}: sound not found'.format(argv[0]))

    data.reply('{} : created {}'.format(target, res[2]))
    data.reply('   : author {}'.format(res[1]))

    if res[3] == 'unknown':
        data.reply('   : unknown source'.format(res[3]))
    else:
        data.reply('   : <a href="{}">source</a>'.format(res[3]))

    data.reply('   : start {}'.format(res[4]))
    data.reply('   : length {}'.format(res[5]))
