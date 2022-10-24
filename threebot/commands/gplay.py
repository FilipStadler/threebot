# Group play command.

import random

desc = 'Plays a random sound from a group.'
usage = 'gplay <GROUPNAME>'

def execute(data, argv):
    if len(argv) < 1:
        raise Exception('expected argument')

    # check group exists

    # select a random sound
    c = data.db.conn.cursor()
    c.execute('SELECT content FROM groups WHERE groupname=?', [argv[0]])
    
    res = c.fetchall()
    
    if len(res) == 0:
        raise Exception(f'"{argv[0]}": group not found')

    mods = [] if len(argv) < 2 else argv[1:]

    to_play = random.choice(res[0][0].split(':'))

    # Test if sound is an alias or not to determine playing method
    to_play, is_alias = data.util.resolve_sound_or_alias(to_play, True)

    data.commands.execute(data, ['s', to_play] + mods)
