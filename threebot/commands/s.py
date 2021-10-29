# Plays a sound from the local collection.

def execute(data, argv):
    if len(argv) == 0:
        raise Exception('expected argument')
    
    data.audio.play(argv[0])
    data.reply('Playing {}.'.format(argv[0]))