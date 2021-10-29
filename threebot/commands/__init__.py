# Walk through command sources in this directory and initialize them.

import importlib
import os
from os import path

MAX_DEPTH=32

dir_path = os.path.dirname(os.path.realpath(__file__))
command_dict = {}

print('Registering commands..')

for f in os.scandir(dir_path):
    if path.isfile(f.path) and path.basename(f.path) != '__init__.py':
        name = str(path.basename(f.path)).split('.')[0]
        spec = importlib.util.spec_from_file_location(name, str(f.path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, 'execute'):
            raise RuntimeError('Command {} does not have an execute() method!'.format(name))

        if not callable(module.execute):
            raise RuntimeError('Command {} "execute" is not callable!'.format(name))

        print('    > {}'.format(name))
        command_dict[name] = module

print('Registered {} command{}.'.format(
    len(command_dict),
    's' if len(command_dict) > 1 else ''
))

def execute(data, argv, depth=0):
    if depth > MAX_DEPTH:
        raise Exception('maximum command depth exceeded')

    # Try and resolve a built-in command
    if argv[0] in command_dict:
        return command_dict[argv[0]].execute(data, argv[1:])
    
    # Try and resolve an alias
    alias = data.db.resolve_alias(argv[0])

    if alias is None:
        raise Exception('{} is not a recognized command or alias'.format(argv[0]))

    next_argv = alias[1].split(' ') + argv[1:]

    # Drop command indicators from expanded argv
    while next_argv[0][0] == '!':
        next_argv[0] = next_argv[0][1:]

    # Expand alias and recombine arguments
    return execute(data, next_argv, depth + 1)
