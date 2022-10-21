# Bind shorthand.

desc = "Sets the caller's bind entry in the DB to the last sound grabbed by the caller."
usage = "blast"

def execute(data, argv):
    if len(argv) > 0:
        raise Exception('incorrect usage. Usage: !blast #sets last played sound to bind')

    target = None
    hist = data.commands.command_dict['get'].grab_history

    if data.author not in hist:
        raise Exception('no sound grabbed recently')

    target = hist[data.author]
    util.set_bind(data.author, target)
