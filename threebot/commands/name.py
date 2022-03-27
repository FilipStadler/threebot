# Alias shorthand.

desc = "Creates an alias for the last sound grabbed by the caller."
usage = "name [NAME]"

def execute(data, argv):
    if len(argv) < 1:
        raise Exception('expected argument')

    hist = data.commands.command_dict['get'].grab_history

    if data.author not in hist:
        raise Exception('no sound grabbed recently')

    target = hist[data.author]
    data.commands.execute(data, ['alias', argv[0], '!s', target])
