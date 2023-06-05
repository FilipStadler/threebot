# Bot controller.

from . import util
from . import commands
from . import audio
from . import db

import argparse
import os
import pymumble_py3 as pymumble
from pymumble_py3.constants import PYMUMBLE_CLBK_USERCREATED
from pymumble_py3.constants import PYMUMBLE_CLBK_TEXTMESSAGERECEIVED
import re
import sys
from datetime import datetime

# Cursed URL regex
URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

# Default connection parameters.
HOST = os.getenv('THREEBOT_HOST', 'localhost')
PORT = os.getenv('THREEBOT_PORT', 64738)
NAME = os.getenv('THREEBOT_NAME', 'Threebot')
PASS = os.getenv('THREEBOT_PASS', '')

# Parse connection parameters.
parser = argparse.ArgumentParser(description='Threebot')
parser.add_argument('--host', default=HOST, help='Mumble server hostname')
parser.add_argument('--port', default=PORT, help='Mumble server port')
parser.add_argument('--name', default=NAME, help='Name to connect as')
parser.add_argument('--pw', default=PASS, help='Connection password')

args = parser.parse_args()

def run():
    """Starts the bot. Connects to the server and spawns threads."""

    # Connect to server.
    print(f'Connecting to {args.host}:{args.port} as {args.name}')

    conn = pymumble.Mumble(args.host,
                           args.name,
                           port=args.port,
                           password=args.pw,
                           stereo=True)

    conn.set_application_string(args.name)
    conn.start()
    conn.is_ready()

    print('Connected!')

    def message_callback(data):
        """Called when a message is sent to the channel."""

        # define reply helper
        def reply(msg):
            conn.users[data.actor].send_text_message(msg)

        # define bcast helper
        def bcast(msg):
            conn.my_channel().send_text_message(msg)

        # Build message metadata dict
        metadata = lambda: None # cool hack for empty namespace

        metadata.author = conn.users[data.actor].get_property('name')
        metadata.reply = reply
        metadata.bcast = bcast
        metadata.db = db
        metadata.audio = audio
        metadata.util = util
        metadata.commands = commands

        # avoid danger
        if metadata.author == NAME:
            return

        # trim message content, remove HTML
        data.message = data.message.strip()
        data.message = re.sub(r"<[^<>]*>", '', data.message)

        # scrape for links
        urls = re.findall(URL_REGEX, data.message)

        for x in urls:
            print(f'Scraped link: {x[0]} from {metadata.author}')

            try:
                c = db.conn.cursor()
                c.execute('INSERT INTO links VALUES (?, ?, datetime("NOW"))',
                          (x[0], metadata.author))
                db.conn.commit()
            except Exception as e:
                print(f'Link insert failed: {e}')

        # ignore empty messages
        if len(data.message) == 0:
            return

        # test for command indicator
        if data.message[0] != '!': 
            return

        # Write command execution to console
        print(f'{datetime.now()} {metadata.author} > {data.message}')

        # remove command indicator
        data.message = data.message[1:]

        # break message into parts
        parts = list(filter(None, data.message.split(' ')))

        # Try and execute command
        try:
            commands.execute(metadata, parts)
        except Exception as e:
            reply(f'error: {e}')
            bt = sys.exc_info()[1]
            m=f'{datetime.now()} {metadata.author} ! exception in command: {bt}'
            print(m)

    def join_callback(data):
        """Called when a user joins the server."""
        c = db.conn.cursor()

        # Log join to console
        print(f'{datetime.now()} > {data.get_property("name")} joined')

        # check if user has greeting
        c.execute('SELECT * FROM greetings WHERE username=?',
                  [data.get_property('name')])

        res = c.fetchone()

        if res is not None:
            try:
                util.play_sound_or_alias(res[1])
            except Exception as e:
                data.send_text_message(f'Error in greeting: {str(e)}')
        else:
            # No greeting, play random sound
            try:
                target = db.random_sound()
                util.play_sound_or_alias(target)

                m = f'Random greeting: {target} (!greeting to update)'
                data.send_text_message(m)

            except Exception as e:
                m = f'Unexpected greeting failure: {str(e)}'
                data.send_text_message(m)

    # Bind connection callbacks
    conn.callbacks.add_callback(PYMUMBLE_CLBK_TEXTMESSAGERECEIVED,
                                message_callback)

    conn.callbacks.add_callback(PYMUMBLE_CLBK_USERCREATED, join_callback)

    # Start audio thread
    audio.start(conn)

    # Basic CLI
    while True:
        print('> ', end='')

        inp_raw = input()
        inp = inp_raw.strip().split(' ')

        if len(inp) < 1 or len(inp[0]) < 1:
            continue

        metadata = lambda: None
        metadata.author = 'Threebot'
        metadata.db = db
        metadata.reply = lambda msg: print(msg)
        metadata.bcast = lambda msg: conn.my_channel().send_text_message(msg)
        metadata.audio = audio
        metadata.util = util

        if inp[0] == '!exit':
            print('Terminating..')
            break

        if inp[0][0] == '!':
            try:
                commands.execute(metadata, inp)
            except Exception as e:
                print(f'Error: {e}')

        conn.my_channel().send_text_message(inp_raw)

    conn.my_channel().send_text_message('Bye!')

    audio.stop()
    conn.stop()

    print('Terminated bot.')
