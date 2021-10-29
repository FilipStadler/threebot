# Version command

usage = 'Gets the current bot version.'

import pkg_resources

def execute(data, argv):
    data.reply('Bot version: {}'.format(pkg_resources.get_distribution('threebot').version))