# Sound play command.

desc = "Plays a sound from the local collection."
usage = "s [CODE]"

def execute(data, argv):
    target = data.db.random_sound() if len(argv) < 1 else argv[0]
    
    data.audio.play(target)
    data.reply('Playing {}.'.format(target))
