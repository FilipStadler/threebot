# Alias delete command.

desc = 'Deletes an alias.'
usage = 'delalias <aliasname>'

def execute(data, argv):
    # delete an alias

    if len(argv) < 1:
        raise Exception('expected argument')

    res = data.db.resolve_alias(argv[0])

    if res is None:
        raise Exception('"{0}": alias not found'.format(argv[0]))
    else:
        c = data.db.conn.cursor()
        c.execute('DELETE FROM aliases WHERE commandname=?', [argv[0]])
        data.db.conn.commit()

        data.reply('Deleted alias "{0}".'.format(argv[0]))