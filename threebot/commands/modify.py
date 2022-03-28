# Sound modification command.

desc = "Modifies an existing sound."
usage = "modify SOUND <length/start> [+-]VALUE"

def execute(data, argv):
    if len(argv) < 3:
        raise Exception('insufficient arguments')

    argv[1] = argv[1].lower()

    if argv[1][0] != 'l' and argv[1][0] != 's':
        raise Exception('invalid mode, must be one of "length", "start"')

    target, is_alias = data.util.resolve_sound_or_alias(argv[0])

    # query sound information
    c = data.db.conn.cursor()
    c.execute('SELECT * FROM sounds WHERE soundname=?', [target])

    res = c.fetchone()

    if not res:
        raise Exception('{}: sound not found'.format(argv[1]))

    res = list(res) # make mutable

    if res[3] == 'unknown':
        raise Exception('{}: no source info (too old), can\'t modify')

    # modify grab parameters
    mode = 5 if argv[1][0] == 'l' else 4

    if argv[2][0] == '+':
        res[mode] += float(argv[2][1:])
    elif argv[2][0] == '-':
        res[mode] -= float(argv[2][1:])
    else:
        res[mode] -= float(argv[2])

    # try to grab new sound
    data.commands.execute(data, ['get', res[3], str(res[4]), str(res[5])])

    # remove old sound from database
    data.commands.execute(data, ['rm', target])

    # if aliased, re-define target
    if is_alias:
        data.commands.execute(data, ['delalias', argv[0]])
        data.commands.execute(data, [
            'alias',
            argv[0],
            's',
            data.commands.command_dict['get'].grab_history[data.author]
        ])
