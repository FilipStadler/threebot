import sqlite3

# Connect to database.
print('Connecting to local database..')
conn = sqlite3.connect('threebot.db', check_same_thread=False)
print('Connected.')

# Apply table schema.
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS links ( dest TEXT UNIQUE, author TEXT, timestamp DATETIME )')
c.execute('CREATE TABLE IF NOT EXISTS pasta ( pastaname TEXT UNIQUE, content TEXT, author TEXT, timestamp DATETIME )')
c.execute('CREATE TABLE IF NOT EXISTS aliases ( commandname TEXT UNIQUE, action TEXT, author TEXT, timestamp DATETIME )')
c.execute('CREATE TABLE IF NOT EXISTS sounds ( soundname TEXT UNIQUE, author TEXT, timestamp DATETIME, source TEXT, start FLOAT, len FLOAT )')
c.execute('CREATE TABLE IF NOT EXISTS greetings ( username TEXT UNIQUE, greeting TEXT )')
c.execute('CREATE TABLE IF NOT EXISTS binds ( username TEXT UNIQUE, bind TEXT )')
c.execute('CREATE TABLE IF NOT EXISTS groups ( groupname TEXT UNIQUE, content TEXT, author TEXT, timestamp DATETIME )')
c.execute('CREATE TABLE IF NOT EXISTS cycles ( sound TEXT, author TEXT )')

# Print some database stats.
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM sounds')
print('{} sound entries in database.'.format(c.fetchone()[0]))

def resolve_alias(name):
    """Resolves an alias to a sound code.

    Parameters
    ----------
    name : str
        The alias to resolve.

    Returns
    -------
    str
        The sound code that the alias resolves to, or None if the alias
        does not exist.
    """
    c = conn.cursor()
    c.execute('SELECT * FROM aliases WHERE commandname=?', [name])
    return c.fetchone()

def random_sound():
    """Returns a random sound code.

    Returns
    -------
    str
        A random sound code.

    Raises
    ------
    RuntimeError
        If there are no sounds in the database.
    """
 
    c = conn.cursor()
    c.execute('SELECT * FROM sounds ORDER BY random() LIMIT 1')

    res = c.fetchall()

    if len(res) < 1:
        raise RuntimeError('No sounds available')

    return res[0][0]
