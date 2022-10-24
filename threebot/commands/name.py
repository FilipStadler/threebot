# Alias shorthand.

desc = "Aliases a recent grabbed song, or by name."
usage = "name <NAME> [SOUND]"

def execute(data, argv):
    if len(argv) < 1:
        raise Exception('expected argument')

    target = None

    if len(argv) > 1:
        target = data.util.resolve_sound_or_alias(argv[1])
    else:
        hist = data.commands.command_dict['get'].grab_history

        if data.author not in hist:
            raise Exception('no sound grabbed recently')

        target = hist[data.author]

    data.commands.execute(data, ['alias', argv[0], '!s', target])
