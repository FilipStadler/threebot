# Custom bind command.

desc = 'Plays your bind sound.'
usage = 'bind'

def execute(data, argv):
    if len(argv) < 1:
        raise Exception('expected argument')

    # search for user bind
    c = data.db.conn.cursor()
    c.execute('SELECT name FROM binds WHERE username=?', [data.author])

    results = c.fetchone()

    if results is None:
        raise Exception('Your bind is not set! Assign it with \'!bind\'.')

    data.util.play_sound_or_alias(results[0])
