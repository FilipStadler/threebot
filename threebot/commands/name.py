# Alias shorthand.

desc = "Creates an alias for a specific sound, or the last sound grabbed by the caller."
usage = "name <NAME> [SOUND]"

def execute(data, argv):
    if len(argv) < 1:
        raise Exception('expected argument')

    target = None

    if len(argv) > 1:
        target = util.resolve_sound_or_alias(argv[1])
    else:
        hist = data.commands.command_dict['get'].grab_history

        if data.author not in hist:
            raise Exception('no sound grabbed recently')

        target = hist[data.author]

    data.commands.execute(data, ['alias', argv[0], '!s', target])
