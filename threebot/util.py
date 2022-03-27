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

def resolve_sound_or_alias(name):
    """Resolves a SOUND input to a sound name. Returns a pair (code, is_alias)"""
    c = db.conn.cursor()

    # try and resolve as an alias
    c.execute('SELECT * FROM aliases WHERE commandname=?', [name])

    res = c.fetchall()

    if len(res) > 0:
        # check that the alias plays a sound
        action = res[0][1].split(' ')

        if action[0] != '!s' and action[0] != 's':
            raise Exception('"{0}" aliases to "{1}" which does not play a sound'.format(name, res[0][1]))

        return action[1], True

    # check if sound is valid code
    c.execute('SELECT * FROM sounds WHERE soundname=?', [name])

    res = c.fetchall()

    if len(res) < 1:
        raise Exception('"{0}" is not a recognized alias or sound'.format(name))

    return name, False

def play_sound_or_alias(name):
    """Plays a sound either by code or alias."""
    audio.play(resolve_sound_or_alias(name))
