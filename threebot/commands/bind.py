# Custom bind command.

desc = 'Plays your bind sound. Rebinds on input.'
usage = 'bind [CODE|ALIAS] [MODS]'
def execute(data, argv):
    if len(argv) < 1:
        # search for user bind
        c = data.db.conn.cursor()
        c.execute('SELECT bind FROM binds WHERE username=?', [data.author])

        results = c.fetchone()

        if results is None:
            raise Exception('No bind set! Usage: bind [CODE|ALIAS] [MODS]')

        parts = results[0].split(' ')

        mods = []
        if len(parts) > 1:
            mods = parts[1:]

        data.util.play_sound_or_alias(parts[0], mods)
        data.reply(f'Playing bind: {" ".join(parts)}')
        return

    # collect mods
    comb = ' '.join(argv)

    data.util.set_bind(data.author, comb)
    data.reply(f'Set bind to {comb}')
