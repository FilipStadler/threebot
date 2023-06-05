# Audio controller.

import os
import pyaudio
import subprocess as sp
import threading

# Audio data format
CHUNK=1024
FORMAT=pyaudio.paInt16
CHANNELS = 2
RATE = 48000

audio_thread_running = False
audio_thread_obj = None

# Sound history buffer. history[0] points to the most recently played sound.
history = []
HISTORY_LEN = 6

def audio_thread(mumble_conn):
    """Audio stream. This method is run on a separate thread and continuously
       reads audio data from the microphone and writes it to the Mumble server.
       """
    global audio_thread_running
    audio_thread_running = True

    # Open the pulse fifo stream and send chunks to the server as they come through.
    
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    while audio_thread_running:
        # don't add zero chunks
        chunk = stream.read(CHUNK)
        zero = True
        for b in chunk:
            if b:
                zero = False
                break

        if not zero:
            mumble_conn.sound_output.add_sound(chunk)

def start(mumble_conn):
    """Launches the audio thread."""
    global audio_thread_running
    global audio_thread_obj

    if audio_thread_running:
        raise RuntimeError('Audio thread already running!')

    audio_thread_obj = threading.Thread(target=audio_thread, args=(mumble_conn,), daemon=True)
    audio_thread_obj.start()
    print('Started audio thread.')

def stop():
    """Terminates the audio thread."""
    global audio_thread_running
    global audio_thread_obj

    if not audio_thread_running:
        raise RuntimeError('Audio thread not running!')
    
    audio_thread_running = False
    audio_thread_obj.join()
    audio_thread_obj = None

    print('Joined audio thread.')

def play(code, mods=[]):
    """Plays a sound with zero or more modifiers applied. May use mpg123
       or ffmpeg to play the sound depending on whether any modifiers are
       present."""

    if type(code) != str:
        raise TypeError('play(): code must be a string')

    if type(mods) != list:
        raise TypeError('play(): mods must be a list')

    filepath = 'sounds/%s.mp3' % code

    history.insert(0, code)
    
    while len(history) > HISTORY_LEN:
        history.pop()

    if not os.path.exists(filepath):
        raise Exception('Sound {} not found.'.format(code))

    if len(mods) < 1:
        return sp.Popen(['mpg123', filepath], stdout=sp.DEVNULL, stderr=sp.DEVNULL)

    modfilters = {
        'fast': ['atempo=2.0'],
        'slow': ['atempo=0.65'],
        'muffle': ['lowpass=f=200'],
        'chorus': ['chorus=0.7:0.9:55:0.4:0.25:2'],
        'bass': ['bass=g=40'],
        'echo': ['aecho=1:1:1200:0.25'],
        'loud': ['volume=5'],
        'reverse': ['areverse'],
        'up': ['asetrate=48000*1.25,aresample=48000,atempo=1/1.25'],
        'down': ['asetrate=48000/2,aresample=48000,atempo=2'],
    }

    args = ['ffmpeg', '-i', filepath]
    
    filters=[]

    for m in mods:
        filters.extend(modfilters.get(m, []))

    filters.extend(['dynaudnorm=p=1'])
    args.extend(['-filter:a', ','.join(filters)])
    args.extend(['-f', 'mp3', '-'])

    decoder = sp.Popen(args, stdout=sp.PIPE, stderr=sp.DEVNULL)
    player = sp.Popen(['mpv', '-vo', 'null', '-'], stdin=decoder.stdout, stdout=sp.DEVNULL)
