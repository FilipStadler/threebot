# Custom bind command.

desc = 'Plays your bind sound.'
usage = 'bind'

def execute(data, argv):
    # search for user bind
    c = data.db.conn.cursor()
    c.execute('SELECT bind FROM binds WHERE username=?', [data.author])

    results = c.fetchone()

    if results is None:
        raise Exception('Your bind is not set! Assign it with \'!bind\'.')

    data.util.play_sound_or_alias(results[0])
    data.reply('Playing bind: {}'.format(results[0]))
