# Alias delete command.

desc = 'Deletes an alias.'
usage = 'delalias <ALIASNAME>'

def execute(data, argv):
    # delete an alias

    if len(argv) < 1:
        raise Exception('expected argument')

    res = data.db.resolve_alias(argv[0])

    if res is None:
        raise Exception('"{argv[0]}": alias not found')
    else:
        c = data.db.conn.cursor()
        c.execute('DELETE FROM aliases WHERE commandname=?', [argv[0]])
        data.db.conn.commit()

        data.reply(f'Deleted alias "{argv[0]}".')
