# Sound delete command.

import os

desc = 'Deletes a sound clip.'
usage = 'delsound <CODE>'

def execute(data, argv):
    # delete a sound

    if len(argv) < 1:
        raise Exception('expected argument')

    if os.path.exists(f'sounds/{argv[0]}.mp3'):
        c = data.db.conn.cursor()
        c.execute('DELETE FROM sounds WHERE soundname=?', [argv[0]])
        data.db.conn.commit()

        os.unlink('sounds/{0}.mp3'.format(argv[0]))
        data.reply('Deleted sound {0}.'.format(argv[0]))
    else:
        raise Exception(f'"{argv[0]}": sound not found')
