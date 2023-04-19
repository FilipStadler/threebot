# Sound play command.

desc = "Grooves it up boi."
usage = "s [CODE [{normal|fast|slow|muffle}]]"

def execute(data, argv):
    target = data.db.random_sound() if len(argv) < 1 else argv[0]

    mods = [] if len(argv) < 2 else argv[1:]

    snd = data.util.resolve_sound_or_alias(target)
    
    data.audio.play(snd, mods)
    data.reply('Playing {}.'.format(snd))

    data.commands.execute(data, ['jam'])
    data.reply('It\'s groovin time')
