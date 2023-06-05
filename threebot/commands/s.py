# Sound play command.

desc = "Plays a sound from the local collection."
usage = "s [CODE] [normal|fast|slow|muffle]*"

def execute(data, argv):
    target = data.db.random_sound() if len(argv) < 1 else argv[0]

    mods = [] if len(argv) < 2 else argv[1:]
    
    data.audio.play(target, mods)
    data.reply('Playing {}.'.format(target))
