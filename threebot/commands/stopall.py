# Stopsounds command.

import os

desc = 'Stops all playing sounds.'

def execute(data, argv):
    os.system('killall mpv')
    os.system('killall mpg123')
