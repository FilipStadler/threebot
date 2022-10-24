# Alias command.

desc = 'Defines a new alias.'
usage = 'alias <ALIASNAME> <COMMAND>'

def execute(data, argv):
    if len(argv) < 2:
        raise Exception(f'expected 2 arguments, found {len(argv)}')

    commandname = argv[0]
    action = ' '.join(argv[1:])

    # check if alias already exists
    if data.db.resolve_alias(commandname) is not None:
        raise Exception(f'alias "{commandname}" already exists!')

    # create new alias
    c = data.db.conn.cursor()
    param = (commandname, action, data.author)
    c.execute('INSERT INTO aliases VALUES (?, ?, ?, datetime("NOW"))', param)
    data.db.conn.commit()

    data.reply('Created alias "{0}" => "{1}".'.format(commandname, action))
