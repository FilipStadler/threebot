# Sound grab command.

import os
import random
import subprocess as sp

desc = 'Grabs a sound clip from YouTube or other internet media source.'
usage = 'get <URL> <[[HR:]MN:]SEC> <DURATION>'

def execute(data, argv):
    if len(argv) < 3:
        raise Exception('get: expected 3 arguments, found {0}'.format(len(argv)))

    # define name generator
    def namegen():
        output = ''

        for i in range(4):
            output += chr(65 + random.randint(0, 25))

        return output

    # find a new ID
    name = namegen()

    while os.path.exists('sounds/{0}.mp3'.format(name)):
        name = namegen()

    # clip a youtube video
    command = ['youtube-dl', '-x',
                '--audio-format', 'mp3',
                '-o', 'sounds/{0}.tmp.mp3'.format(name), argv[0]]
    ytdl = sp.check_output(command, stderr=sp.PIPE)

    # convert clip to desired bounds
    command = ['ffmpeg', '-i', 'sounds/{0}.tmp.mp3'.format(name),
                '-ss', argv[1], '-t', argv[2], 'sounds/{0}.mp3'.format(name)]

    fmpg = sp.check_output(command, stderr=sp.PIPE)

    # remove temporary file
    os.unlink('sounds/{0}.tmp.mp3'.format(name))

    # clip OK, add to database
    c = data.db.conn.cursor()
    c.execute('INSERT INTO sounds VALUES (?, ?, datetime("NOW"), ?, ?, ?)', (name, data.author, argv[0], argv[1], argv[2]))
    data.db.conn.commit()

    data.reply('Created new clip {0}.'.format(name))
    data.audio.play(name)
