import sqlite3

# Connect to database.
print('Connecting to local database..')
conn = sqlite3.connect('threebot.db', check_same_thread=False)
print('Connected.')

# Print some database stats.
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM sounds')
print('{} sound entries in database.'.format(c.fetchone()[0]))

# Apply table schema.
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS links ( dest TEXT UNIQUE, author TEXT, timestamp DATETIME )')
c.execute('CREATE TABLE IF NOT EXISTS aliases ( commandname TEXT UNIQUE, action TEXT, author TEXT, timestamp DATETIME )')
c.execute('CREATE TABLE IF NOT EXISTS sounds ( soundname TEXT UNIQUE, author TEXT, timestamp DATETIME )')
c.execute('CREATE TABLE IF NOT EXISTS greetings ( username TEXT UNIQUE, greeting TEXT )')
c.execute('CREATE TABLE IF NOT EXISTS groups ( groupname TEXT UNIQUE, content TEXT, author TEXT, timestamp DATETIME )')

def resolve_alias(name):
    """
        Returns an array [commandname, action, author, timestamp] if an alias
        with name <name> exists, or None if it does not.
    """
    c = conn.cursor()
    c.execute('SELECT * FROM aliases WHERE commandname=?', [name])
    return c.fetchone()

def random_sound():
    """Returns a random sound code. Raises an exception if no sounds are
       available."""

    c = conn.cursor()
    c.execute('SELECT * FROM sounds ORDER BY random() LIMIT 1')

    res = c.fetchall()

    if len(res) < 1:
        raise RuntimeError('No sounds available')

    return res[0][0]
