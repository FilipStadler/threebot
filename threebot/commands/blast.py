# Bind shorthand.

desc = "Sets the caller's bind entry in the DB to the last sound played by the caller."
usage = "blast"

def execute(data, argv):
    if len(argv) > 0:
        e = 'incorrect usage. Usage: !blast #sets last played sound to bind'
        raise Exception(e)

    target = None
    hist = data.audio.history

    if not hist:
        raise Exception('no sound played recently')

    target = hist[0]
    data.util.set_bind(data.author, target)

    data.reply(f'Set bind to {target}')
