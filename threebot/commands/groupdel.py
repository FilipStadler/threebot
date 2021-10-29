# Group remove command.

desc = 'Removes a sound from a group.'
usage = 'groupdel <GROUPNAME> <CODE|ALIAS>'

def execute(data, argv):
    c = data.db.conn.cursor()

    if len(argv) < 2:
        raise Exception('expected [group] [sound]')

    if ':' in argv[1]:
        raise Exception('no codes with \':\' allowed')

    c.execute('SELECT content FROM groups WHERE groupname=?', [argv[0]])

    res = c.fetchall()

    if len(res) == 0:
        data.reply('Group {} not found'.format(argv[0]))
    else:
        old_content = res[0][0].split(':')

        if argv[1] in old_content:
            old_content.remove(argv[1])
        else:
            data.reply('WARNING: {} not in group'.format(argv[1]))

        new_content = ':'.join(old_content)

        if len(new_content) > 0:
            c.execute('UPDATE groups SET content=? WHERE groupname=?', [new_content, argv[0]])
            data.reply('Removed {} from group {}.'.format(argv[1], argv[2]))
        else:
            c.execute('DELETE FROM groups WHERE groupname=?', [argv[0]])

        data.db.conn.commit()