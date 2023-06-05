# Custom bind command.

desc = 'Cycles your bind through your saved "cycle" clips.'
usage = 'cycle [add CODE/ALIAS remove CODE/ALIAS]'

def execute(data, argv):
    if len(argv) < 1:
        # apply cycle
        # search for user bind
        c = data.db.conn.cursor()
        c.execute('SELECT sound FROM cycles WHERE author=?', [data.author])

        cycle_binds = c.fetchall()

        if cycle_binds is None:
            data.reply('no bind cycles saved, use "cycle add" to add some')
            return

        c.execute('SELECT bind FROM binds WHERE username=?', [data.author])
        current_bind = c.fetchone()

        next_bind = cycle_binds[0][0]

        if current_bind is not None:
            for i in range(len(cycle_binds)):
                if cycle_binds[i][0] == current_bind[0]:
                    next_bind = cycle_binds[(i + 1) % len(cycle_binds)][0]

        data.util.set_bind(data.author, next_bind)
        data.reply(f'Set bind to {next_bind}')
        return

    elif argv[0] == 'add':
        if len(argv != 2):
            raise Exception('usage: ' + usage)

        data.util.resolve_sound_or_alias(argv[1])
        c = data.db.conn.cursor()
        c.execute('INSERT INTO cycles VALUES (?, ?)', [argv[1], data.author])
        data.db.conn.commit()
        data.reply(f'added {argv[1]} to cycle')

    elif argv[0] == 'remove':

        if len(argv != 2):
            raise Exception('usage: ' + usage)

        c = data.db.conn.cursor()
        c.execute('DELETE FROM cycles WHERE author=? AND sound=?', [data.author, argv[1]])
        data.db.conn.commit()
        data.reply(f'deleted {argv[1]} from cycle')

    else:
        raise 'invalid usage'
