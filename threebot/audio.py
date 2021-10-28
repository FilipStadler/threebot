# Connection audio controller.

import os
import pyaudio
import threading
import subprocess as sp

CHUNK=1024
FORMAT=pyaudio.paInt16
CHANNELS = 1
RATE = 48000

audio_thread_running = False
audio_thread_obj = None

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

    audio_thread_obj = threading.Thread(target=(audio_thread, mumble_conn), daemon=True)
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

def play(code):
    filepath = 'sounds/%s.mp3' % code

    if not os.path.exists(filepath):
        raise Exception('Sound {} not found.'.format(code))

    command = ['mpg123', filepath]
    sp.run(command, check=True)