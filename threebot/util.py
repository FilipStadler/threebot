# Generic utilities for use by all commands.

from . import audio
from . import db

def into_pages(headers, rows, rows_per_page=32):
    pages = []

    while len(rows) > 0:
        msg = '<table><tr>'
        
        for h in headers:
            msg += '<th>{0}</th>'.format(h)

        msg += '</tr>'

        for r in rows[0:rows_per_page]:
            msg += '<tr>'

            for el in r:
                msg += '<td>{0}</td>'.format(el)

        msg += '</table>'
        pages.append(msg)

        rows = rows[rows_per_page:]

    return pages

def play_sound_or_alias(name):
    """Tries to play a sound or an alias to a sound."""
    c = db.conn.cursor()

    # check if sound is valid code
    c.execute('SELECT * FROM sounds WHERE soundname=?', [name])

    if len(c.fetchall()) > 0:
        audio.play(name)
    else:
        # try and resolve as an alias
        c.execute('SELECT * FROM aliases WHERE commandname=?', [name])

        r2 = c.fetchall()

        if len(r2) == 0:
            raise Exception('"{0}" is not a recognized sound or alias'.format(name))
        else:
            # check that the alias plays a sound
            action = r2[0][1].split(' ')

            if action[0] != '!s':
                raise Exception('"{0}" aliases to "{1}" which does not play a sound'.format(name, r2[0][1]))
            else:
                audio.play(action[1])