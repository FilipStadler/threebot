# Alias command.

desc = 'Defines a new alias.'
usage = 'alias <ALIASNAME> <COMMAND>'

def execute(data, argv):
    if len(argv) < 2:
        raise Exception('expected 2 arguments, found {0}'.format(len(argv) - 1))

    commandname = argv[0]
    action = ' '.join(argv[1:])

    # check if alias already exists
    if data.db.resolve_alias(commandname) is not None:
        raise Exception('destination alias "{0}" already exists!'.format(commandname))

    # create new alias
    c = data.db.conn.cursor()
    c.execute('INSERT INTO aliases VALUES (?, ?, ?, datetime("NOW"))', (commandname, action, data.author))
    data.db.conn.commit()

    data.reply('Created alias "{0}" => "{1}".'.format(commandname, action))