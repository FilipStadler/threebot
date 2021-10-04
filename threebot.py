#!/usr/bin/env python3.8
# threebot source
# -*- coding: utf-8 -*-

import argparse
import os
import pymumble_py3 as pymumble
import pyaudio
import random
import re
import select
import subprocess as sp
import sys
import sqlite3
import time
import threading

# default configuration

HOST = os.getenv('THREEBOT_HOST', 'localhost')
PORT = os.getenv('THREEBOT_PORT', 64738)
NAME = os.getenv('THREEBOT_NAME', 'Threebot')
PASS = os.getenv('THREEBOT_PASS', '')

TMP_VOICEFILE = '/tmp/voice.mp3'

# parse command-line arguments

parser = argparse.ArgumentParser(description='Threebot')
parser.add_argument('--host', default=HOST, help='Mumble server hostname')
parser.add_argument('--port', default=PORT, help='Mumble server port')
parser.add_argument('--name', default=NAME, help='Name to connect as')
parser.add_argument('--pw', default=PASS, help='Connection password')

args = parser.parse_args()

# connect to db

print('Connecting to local db.')
db = sqlite3.connect('threebot.db', check_same_thread=False)
print('Connected.')

# cursed regex

URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

# apply schema

c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS links ( dest TEXT UNIQUE, author TEXT, timestamp DATETIME )')
c.execute('CREATE TABLE IF NOT EXISTS aliases ( commandname TEXT UNIQUE, action TEXT, author TEXT, timestamp DATETIME )')
c.execute('CREATE TABLE IF NOT EXISTS sounds ( soundname TEXT UNIQUE, author TEXT, timestamp DATETIME )')
c.execute('CREATE TABLE IF NOT EXISTS greetings ( username TEXT UNIQUE, greeting TEXT )')

# start connection

print('Connecting to {0}:{1} as {2}'.format(args.host, args.port, args.name))
conn = pymumble.Mumble(args.host, args.name, port=args.port, password=args.pw)
conn.set_application_string('Threebot')
conn.start()
conn.is_ready()
print('Connected!')

# define player functions

ffmpeg_proc = None

CHUNK=1024
FORMAT=pyaudio.paInt16
CHANNELS = 1
RATE = 48000

def audio_thread():
    # Open the pulse fifo stream and send chunks to the server as they come through.
    print('started thread')
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    while True:
        # don't add zero chunks
        chunk = stream.read(CHUNK)
        zero = True
        for b in chunk:
            if b:
                zero = False
                break

        if not zero:
            conn.sound_output.add_sound(chunk)

# start audio thread
audio_thread_obj = threading.Thread(target=audio_thread, daemon=True)
audio_thread_obj.start()

# init sound history
HISTORY_LEN = 6
history = []

def play_sound(name):
    filepath = 'sounds/%s.mp3' % name

    if not os.path.exists(filepath):
        raise Exception('File "{0}" not found.'.format(filepath))

    #command = ['mpv', '-ao', 'pulse', '-af', 'loudnorm=I=-25:TP=-1.5:LRA=1', '--really-quiet', filepath]
    command = ['mpg123', filepath]
    #command = ['ffmpeg', '-i', filepath, '-f', 'pulse', '-device', 'playback-device', 'threebot']
    print('Playing %s' % filepath)
    sp.run(command, check=True)

    history.append(name)
    while len(history) > HISTORY_LEN:
        history.pop(0)

# define alias lookup

def lookup_alias(commandname):
    c = db.cursor()
    c.execute('SELECT * FROM aliases WHERE commandname=?', [commandname])
    return c.fetchone()

# helper for splitting up tables
def split_table(header, rows, rowsplit=64):
    messages = []

    while len(rows) > 0:
        msg = '<table><tr>'
        
        for h in header:
            msg += '<th>{0}</th>'.format(h)

        msg += '</tr>'

        for r in rows[0:rowsplit]:
            msg += '<tr>'

            for el in r:
                msg += '<td>{0}</td>'.format(el)

        msg += '</table>'
        messages.append(msg)

        rows = rows[rowsplit:]

    return messages

# prepare message callback

def message_callback(data, depth=0):
    # define reply helper
    def reply(msg):
        conn.users[data.actor].send_text_message(msg)

    # avoid alias overflows
    if depth > 16:
        reply('Maximum alias depth exceeded.')
        return

    # trim message content
    data.message = data.message.strip()

    # remove HTML
    data.message = re.sub(r"<[^<>]*>", '', data.message)

    # grab author
    author = conn.users[data.actor].get_property('name')

    # scrape for links
    urls = re.findall(URL_REGEX, data.message)

    for x in urls:
        print('Scraped link: {0} from {1}'.format(x[0], author))

        try:
            c = db.cursor()
            c.execute('INSERT INTO links VALUES (?, ?, datetime("NOW"))', (x[0], author))
            db.commit()
        except sqlite3.IntegrityError:
            print('Link already present, ignoring')

    # ignore empty messages
    if len(data.message) == 0:
        return

    # test for command indicator
    if data.message[0] != '!': 
        return

    # remove command indicator
    data.message = data.message[1:]

    # break message into parts
    parts = list(filter(None, data.message.split(' ')))

    try:
        if parts[0] == 'ping':
            reply('Pong!')
        elif parts[0] == 'rl':
            # choose a random link
            c = db.cursor()
            c.execute('SELECT * FROM links ORDER BY random() LIMIT 1')

            row = c.fetchone()

            if row is None:
                reply('No links!')
            else:
                conn.my_channel().send_text_message('A gift from <a href="{0}">{1}</a>'.format(row[1], row[0]))
        elif parts[0] == 'history':
            reply('Recent sounds: {}'.format(', '.join(reversed(history))))
        elif parts[0] == 'help':
            resp = '<table><tr><th>Command</th><th>Description</th><th>Usage</th></tr>'

            commands = [
                {
                    'name': 'alias',
                    'desc': 'Creates a command alias.',
                    'usage': '&lt;Alias&gt; &lt;Action&gt;',
                },
                {
                    'name': 'aliases',
                    'desc': 'Lists available aliases.',
                    'usage': '',
                },
                {
                    'name': 'delalias',
                    'desc': 'Deletes an alias.',
                    'usage': '&lt;Alias&gt;',
                },
                {
                    'name': 'delsound',
                    'desc': 'Deletes a sound.',
                    'usage': '&lt;Sound&gt;',
                },
                {
                    'name': 'get',
                    'desc': 'Clips a YouTube video into a new sound.',
                    'usage': '&lt;URL&gt; &lt;Timestamp&gt; &lt;Duration&gt;',
                },
                {
                    'name': 'greeting',
                    'desc': 'Changes or removes your personal greeting sound.',
                    'usage': '[Sound]',
                },
                {
                    'name': 'help',
                    'desc': 'Lists commands, or gets information on a certain command.',
                    'usage': '[Command]',
                },
                {
                    'name': 'ping',
                    'desc': 'Responds with "Pong!"',
                    'usage': '',
                },
                {
                    'name': 'rl',
                    'desc': 'Gets a random link and sends it to the channel.',
                    'usage': '',
                },
                {
                    'name': 's',
                    'desc': 'Plays a random sound to the server, or a specific sound.',
                    'usage': '[Sound]',
                },
                {
                    'name': 'sounds',
                    'desc': 'Lists available sounds, or gets information on a specific sound.',
                    'usage': '[Sound]',
                },
                {
                    'name': 'stopall',
                    'desc': 'Stops any currently playing sounds.',
                    'usage': '',
                },
                {
                    'name': 'history',
                    'desc': 'Lists recently played sounds.',
                    'usage': '',
                },
            ]

            if len(parts) > 1:
                found = False
                for cmd in commands:
                    if cmd['name'] == parts[1]:
                        resp += '<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>'.format(cmd['name'], cmd['desc'], cmd['usage'])
                        found = True

                if not found:
                    raise Exception('help: unknown command "{0}"'.format(parts[1]))
            else:
                for cmd in commands:
                    resp += '<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>'.format(cmd['name'], cmd['desc'], cmd['usage'])

            resp += '</table>'
            reply(resp)
        elif parts[0] == 's':
            to_play = None

            if len(parts) > 1:
                # play a specific sound
                to_play = parts[1]
            else:
                # select a random sound
                c = db.cursor()
                c.execute('SELECT * FROM sounds ORDER BY random() LIMIT 1')
                to_play = c.fetchone()[0]

            reply('Playing {0}.'.format(to_play))
            play_sound(to_play)
        elif parts[0] == 'alias':
            if len(parts) < 3:
                raise Exception('alias: expected 2 arguments, found {0}'.format(len(parts) - 1))

            commandname = parts[1]
            action = ' '.join(parts[2:])

            print('Creating alias: "{0}" => "{1}"'.format(commandname, action))

            # check if alias already exists
            if lookup_alias(commandname) is not None:
                raise Exception('alias: destination alias "{0}" already exists!'.format(commandname))

            # create new alias
            c = db.cursor()
            c.execute('INSERT INTO aliases VALUES (?, ?, ?, datetime("NOW"))', (commandname, action, author))
            db.commit()

            reply('Created alias "{0}" => "{1}".'.format(commandname, action))
        elif parts[0] == 'greeting':
            c = db.cursor()

            if len(parts) > 1:
                # check if username is already in db
                c.execute('SELECT * FROM greetings WHERE username=?', [author])

                if len(c.fetchall()) == 0:
                    c.execute('INSERT INTO greetings VALUES (?, ?)', [author, parts[1]])
                else:
                    c.execute('UPDATE greetings SET greeting=? WHERE username=?', [parts[1], author])

                reply('Set greeting to {0}.'.format(parts[1]))
            else:
                c.execute('DELETE FROM greetings WHERE username=?', [author])
                reply('Removed greeting.')
        elif parts[0] == 'delsound':
            # delete a sound

            if len(parts) < 2:
                raise Exception('delsound: expected argument')

            if os.path.exists('sounds/{0}.mp3'.format(parts[1])):
                c = db.cursor()
                c.execute('DELETE FROM sounds WHERE soundname=?', [parts[1]])
                db.commit()

                os.unlink('sounds/{0}.mp3'.format(parts[1]))
                reply('Deleted sound {0}.'.format(parts[1]))
            else:
                raise Exception('"{0}": sound not found'.format(parts[1]))
        elif parts[0] == 'delalias':
            # delete an alias

            if len(parts) < 2:
                raise Exception('delalias: expected argument')

            res = lookup_alias(parts[1])

            if res is None:
                raise Exception('"{0}": alias not found'.format(parts[1]))
            else:
                c = db.cursor()
                c.execute('DELETE FROM aliases WHERE commandname=?', [parts[1]])
                db.commit()

                reply('Deleted alias "{0}".'.format(parts[1]))
        elif parts[0] == 'aliases':
            # query all aliases
            c = db.cursor()
            c.execute('SELECT * FROM aliases ORDER BY commandname')
            rows = c.fetchall()

            for m in split_table(['Alias', 'Action', 'Author', 'Created'], rows):
                reply(m)
        elif parts[0] == 'sounds':
            c = db.cursor()

            if len(parts) > 1:
                # query a specific sound
                c.execute('SELECT * FROM sounds WHERE soundname=?', [parts[1]])
            else:
                # query all sounds 
                c.execute('SELECT * FROM sounds ORDER BY timestamp DESC')

            rows = c.fetchall()

            for m in split_table(['Sound', 'Author', 'Created'], rows):
                reply(m)
        elif parts[0] == 'get':
            # check args
            if len(parts) < 4:
                raise Exception('get: expected 3 arguments, found {0}'.format(len(parts) - 1))

            # define name generator
            def namegen():
                output = ''

                for i in range(4):
                    output += chr(65 + random.randint(0, 25))

                return output

            # find a new ID
            name = namegen()

            while os.path.exists('sounds/{0}.mp3'.format(name)):
                name = namegen()

            # clip a youtube video
            command = ['youtube-dl', '-x',
                       '--audio-format', 'mp3',
                       '-o', 'sounds/{0}.tmp.mp3'.format(name), parts[1]]
            ytdl = sp.check_output(command, stderr=sp.PIPE)
            #reply(str(ytdl))

            # convert clip to desired bounds
            command = ['ffmpeg', '-i', 'sounds/{0}.tmp.mp3'.format(name),
                        '-ss', parts[2], '-t', parts[3], 'sounds/{0}.mp3'.format(name)]

            fmpg = sp.check_output(command, stderr=sp.PIPE)

            #reply(str(fmpg))

            # remove temporary file
            os.unlink('sounds/{0}.tmp.mp3'.format(name))

            # clip OK, add to database
            c = db.cursor()
            c.execute('INSERT INTO sounds VALUES (?, ?, datetime("NOW"))', (name, author))
            db.commit()

            reply('Created new clip {0}.'.format(name))
            data.message = '!s %s' % name
            return message_callback(data, depth + 1)
        elif parts[0] == 'stopall':
            os.system('killall mpg123')
            reply('Stopping all sounds.')
        else:
            # try and lookup an alias
            res = lookup_alias(parts[0])

            if res is None:
                raise Exception('"{0}": command not found'.format(parts[0]))

            # execute alias
            data.message = res[1] + ' '

            if len(parts) > 1:
                print('adding args: "{0}"'.format(' ' + ' '.join(parts[1:])))
                data.message += ' ' + ' '.join(parts[1:])

            return message_callback(data, depth + 1)

    except sp.CalledProcessError as e:
        reply('Process error: retcode {0}, output {1}'.format(e.returncode, re.sub(r'\\n', '<br />', str(e.stderr))))
    except Exception as e:
        reply('Error: {0}'.format(str(e)))

# define greeting callback

def join_callback(data):
    c = db.cursor()

    # check if user has greeting
    c.execute('SELECT * FROM greetings WHERE username=?', [data.get_property('name')])
    res = c.fetchall()

    try:
        if len(res) == 0:
            c.execute('SELECT * FROM sounds ORDER BY random() LIMIT 1')
            play_sound(c.fetchone()[0])
        else:
            # check if sound is valid code
            c.execute('SELECT * FROM sounds WHERE soundname=?', [res[0][1]])

            if len(c.fetchall()) > 0:
                play_sound(res[0][1])
                data.send_text_message('Playing greeting {0}'.format(res[0][1]))
            else:
                # try and resolve as an alias
                c.execute('SELECT * FROM aliases WHERE commandname=?', [res[0][1]])

                r2 = c.fetchall()

                if len(r2) == 0:
                    data.send_text_message('Error in greeting: "{0}" is not a recognized sound or alias'.format(res[0][1]))
                else:
                    # check that the alias plays a sound
                    action = r2[0][1].split(' ')

                    if action[0] != '!s':
                        data.send_text_message('Error in greeting: "{0}" aliases to "{1}" which does not play a sound'.format(res[0][1], r2[0][1]))
                    else:
                        play_sound(action[1])
    except Exception as e:
        data.send_text_message('Error occurred in greeting: {0}'.format(str(e)))

# add callbacks

conn.callbacks.add_callback(pymumble.constants.PYMUMBLE_CLBK_TEXTMESSAGERECEIVED, message_callback)
conn.callbacks.add_callback(pymumble.constants.PYMUMBLE_CLBK_USERCREATED, join_callback)

# wait for things to happen

while True:
    inp = input()
