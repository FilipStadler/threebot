# Sound information query.

import random

desc = "What the fuck did you say?"
usage = "sinfo [CODE/ALIAS]"

def execute(data, argv):
    if len(argv) > 0:
        if argv[0] in ('new', 'add'):
            pname = random.randint(0, 1000)

            # create a new pasta
            content = ' '.join(argv[1:])
            c = data.db.conn.cursor()
            c.execute('INSERT INTO pasta VALUES (?, ?, ?, datetime("NOW"))', (pname, content, data.author))
            data.db.conn.commit()
            data.reply('created pasta {}'.format(pname))
            data.bcast(content)
            return
        elif argv[0] in ('delete', 'remove'):
            if len(argv) != 2:
                raise 'expected 2 arguments, found ' + str(len(argv))

            pname = argv[1]
            c = data.db.conn.cursor()
            c.execute('DELETE FROM pasta WHERE pastaname = ?', (pname,))
            data.db.conn.commit()
            data.reply('deleted pasta {}'.format(pname))
            return
        else:
            return data.reply('usage: pasta [new CONTENT | delete CODE]')

    # find a pasta
    c = data.db.conn.cursor()
    c.execute('SELECT pastaname, content FROM pasta ORDER BY random() LIMIT 1')

    row = c.fetchone()

    # serve the pasta
    data.reply('pasta {}'.format(row[0]))
    data.bcast(row[1])
