import pyaudio
import wave
import sys
#Code is taken from https://stackoverflow.com/questions/6951046/how-to-play-an
# -audiofile-with-pyaudio
# length of data to read.
chunk = 1024

'''
************************************************************************
      This is the start of the "minimum needed to read a wave"
************************************************************************
'''
# open the file for reading.
import pyaudio
import wave
import sys

class AudioFile:
    chunk = 1024

    def __init__(self, file):
        """ Init audio stream """ 
        self.wf = wave.open(file, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True
        )

    def play(self):
        """ Play entire file """
        data = self.wf.readframes(self.chunk)
        while data != '':
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)
        self.close()

    def close(self):
        """ Graceful shutdown """ 
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

# Usage example for pyaudio
