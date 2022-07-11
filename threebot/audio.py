# Connection audio controller.

import os
import pyaudio
import threading
import subprocess as sp

CHUNK=1024
FORMAT=pyaudio.paInt16
CHANNELS = 2
RATE = 48000

audio_thread_running = False
audio_thread_obj = None

history = []
HISTORY_LEN = 6

def audio_thread(mumble_conn):
    global audio_thread_running
    audio_thread_running = True

    # Open the pulse fifo stream and send chunks to the server as they come through.
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

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
    global audio_thread_running
    global audio_thread_obj

    if audio_thread_running:
        raise RuntimeError('Audio thread already running!')

    audio_thread_obj = threading.Thread(target=audio_thread, args=(mumble_conn,), daemon=True)
    audio_thread_obj.start()
    print('Started audio thread.')

def stop():
    global audio_thread_running
    global audio_thread_obj

    if not audio_thread_running:
        raise RuntimeError('Audio thread not running!')
    
    audio_thread_running = False
    audio_thread_obj.join()
    audio_thread_obj = None

    print('Joined audio thread.')

def play(code, mode='normal'):
    filepath = 'sounds/%s.mp3' % code

    history.insert(0, code)
    
    while len(history) > HISTORY_LEN:
        history.pop()

    if not os.path.exists(filepath):
        raise Exception('Sound {} not found.'.format(code))

    args = ['mpg123']

    if mode == 'normal':
        pass
    elif mode == 'fast':
        args.extend(['-d', '2'])
    elif mode == 'slow':
        args.extend(['-h', '2'])
    elif mode == 'muffle':
        args.extend(['-r', '1500'])
    else:
        raise Exception('unknown playback mode "{}"'.format(mode))

    args.append(filepath)

    sp.Popen(args, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
