# Group add command.

desc = 'Adds a sound to a group.'
usage = 'groupadd <GROUPNAME> <CODE|ALIAS>'

def execute(data, argv):
    c = data.db.conn.cursor()

    if len(argv) < 2:
        raise Exception('expected [group] [sound]')

    if ':' in argv[1]:
        raise Exception('no codes with \':\' allowed')

    c.execute('SELECT content FROM groups WHERE groupname=?', [argv[0]])

    res = c.fetchall()

    if len(res) == 0:
        c.execute('INSERT INTO groups VALUES (?, ?, ?, datetime("NOW"))', [argv[0], argv[1], data.author])
        data.db.conn.commit()
        data.reply('Created new group {}'.format(argv[0]))
    else:
        new_content = ':'.join(res[0][0].split(':') + [argv[1]])
        c.execute('UPDATE groups SET content=? WHERE groupname=?', [new_content, argv[0]])
        data.db.conn.commit()
        data.reply('Added {} to group {}.'.format(argv[1], argv[0]))