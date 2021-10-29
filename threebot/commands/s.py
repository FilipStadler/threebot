# Sound play command.

desc = "Plays a sound from the local collection."
usage = "s [CODE]"

def execute(data, argv):
    target = None

    if len(argv) == 0:
        # pick a random sound
        c = data.db.conn.cursor()
        c.execute('SELECT * FROM sounds ORDER BY random() LIMIT 1')
        target = c.fetchone()[0]
    else:
        target = argv[0]
    
    data.audio.play(target)
    data.reply('Playing {}.'.format(target))
