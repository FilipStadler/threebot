# Sound history command.

desc = 'Queries recent sounds.'

def execute(data, argv):
    data.reply('Recent sounds: {}'.format(', '.join(data.audio.history)))
