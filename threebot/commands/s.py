# Sound play command.

desc = "Plays a sound from the local collection."
usage = "s [CODE [{normal|fast|slow|muffle}]]"

def execute(data, argv):
    target = data.db.random_sound() if len(argv) < 1 else argv[0]

    mode = 'normal'
    if len(argv) > 1:
        mode = argv[1]
    
    data.audio.play(target, mode)
    data.reply('Playing {}.'.format(target))
