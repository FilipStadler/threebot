# Generic utilities for use by all commands.

from . import audio
from . import db

def set_bind(author, name):
    """Sets the bind for a user.

    Parameters
    ----------
    author : str
        The username of the user to set the bind for.
    name : str
        The name of the sound to bind to.
    """
    c = db.conn.cursor()

    base = name.split(' ')[0]

    # verify the bind is a valid sound
    resolve_sound_or_alias(base)

    # check if binding or rebinding
    c.execute('SELECT * FROM binds WHERE username=?', [author])
    results = c.fetchone()
    if results is None:
        c.execute('INSERT INTO binds VALUES (?, ?)', [author, name])
    else:
        c.execute('UPDATE binds SET bind=? WHERE username=?', [name, author])

    db.conn.commit()

def into_pages(headers, rows, rows_per_page=32):
    """Splits a list of rows into pages.

    Parameters
    ----------
    headers : list of str
        The headers for the table.
    rows : list of list of str
        The rows for the table.
    rows_per_page : int, optional
        The number of rows per page, by default 32

    Returns
    -------
    list of str
        A list of HTML tables, each table representing a page.
    """
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

def resolve_sound_or_alias(name, check_alias=False):
    """Resolves a sound or alias to a sound code.

    Parameters
    ----------
    name : str
        The name of the sound or alias to resolve.
    check_alias : bool, optional
        Whether to test if an alias is resolved, by default False

    Returns
    -------
    str
        The sound code that the name resolves to.

    Raises
    ------
    Exception
        If the name does not resolve to a sound or alias, or if the alias
        does not play a sound.
    """
    c = db.conn.cursor()

    # try and resolve as an alias
    c.execute('SELECT * FROM aliases WHERE commandname=?', [name])

    res = c.fetchall()

    if len(res) > 0:
        # check that the alias plays a sound
        action = res[0][1].split(' ')

        if action[0] != '!s' and action[0] != 's':
            raise Exception('"{0}" aliases to "{1}" which does not play a sound'.format(name, res[0][1]))

        if check_alias:
            return action[1], True
        else:
            return action[1]

    # check if sound is valid code
    c.execute('SELECT * FROM sounds WHERE soundname=?', [name])

    res = c.fetchall()

    if len(res) < 1:
        raise Exception('"{0}" is not a recognized alias or sound'.format(name))

    if check_alias:
        return name, False
    else:
        return name

def play_sound_or_alias(name, mods=[]):
    """Play a sound or alias.

    Parameters
    ----------
    name : str
        The name of the sound or alias to play.
    mods : list, optional
        The modifiers to apply to the sound, by default []
    """
    audio.play(resolve_sound_or_alias(name), mods)
