#Joseph Sandler, jsandler, Section B
import pyaudio, aubio, numpy, os
"""
Pitch detection object set up using pyaudio for an input stream via callback
and Aubio to detect and store pitch through callback as an instance attribute
"""

class PitchDetectionObject(object):

    def __init__(self):
        # Opens pyaudio stream as callback and uses aubio to detect pitch
        # Handling of determined pitch found in helper checkNote
        self.pyaudioStreamFormat = pyaudio.paFloat32
        # values are standard/defaults based on PyAudio docs
        self.paChannels = 1
        self.sampleRate = 44100
        self.sampleSize = 1024
        self.tolerance = 0.8 #Tolerance for pitch detection
        self.note = 0
        self.volume = 0


        self.p = pyaudio.PyAudio() #instantialize pyaudio

        self.openStream()

    def openStream(self):
        # Open pyaudio stream as callback
        # print("Opening callback stream...")
        self.stream = self.p.open(format=self.pyaudioStreamFormat,
            channels=self.paChannels,
            rate=self.sampleRate,
            input=True, output=False,
            frames_per_buffer=self.sampleSize,
            stream_callback=self.callback)

    def pitchDetectionInit(self):
        #Initialize pitch detection object from aubio
        pitchDetectionObject = aubio.pitch(hop_size=self.sampleSize)
        pitchDetectionObject.set_unit("midi") #return pitch as midi val
        pitchDetectionObject.set_tolerance(self.tolerance)
        return pitchDetectionObject

    def callback(self, in_data, frame_count, time_info, status_flags):
        # Callback function for  pyAudio stream. Allows pitch detection while
        # other actions take place 
        pitchDetectionObject = self.pitchDetectionInit()
        # Convert pyaudio data into array readable by aubio.
        # *** Not copied exactly, but made with reference to:
        # https://github.com/aubio/aubio/tree/master/python/
        #                                           demos/demo_pyaudio.py

        dataAubio = numpy.frombuffer(in_data, dtype=numpy.float32)

        # Get pitch as midi val by passing in data-returns list of one item
        pitchVal = pitchDetectionObject(dataAubio)[0]
        self.note = int(numpy.around(pitchVal)) # Round to nearest whole value,
        # since people often sing out of tune/cannot sing exact pitches due to
        # vibrato.

        # Volume (energy) detection. Borrowed from nabeel913:
        # https://gist.github.com/nabeel913/344fa7a501f9eef6d6090aa20b00d954
        self.volume = numpy.sum(dataAubio**2)/len(dataAubio)
        self.volume = float("{:6f}".format(self.volume))

        return (in_data, pyaudio.paContinue)



    def closeStream(self):
        #closes stream
        # print("Closing stream...")
        self.stream.close()

    def kill(self):
        # Terminates PyAudio instance
        self.closeStream()
        self.p.terminate()
        self.note = 0

    def getNote(self):
        # Return midi value of current sung pitch
        return self.note

    def pitchInRange(self, lowerBound, upperBound, scale=None):
        # Checks if current pitch is within a certain range of pitches
        # All as midiVals. Also checks optionally if pitch is in given musical 
        # scale given as list of midi vals

        twelveToneScaleLen = 12

        if scale != None:
            #only do this if a scale is given
            if self.note % twelveToneScaleLen not in scale:
                #must mod midival by 12 to get pitch without octave
                return False
        return lowerBound <= self.note <= upperBound

    def volumeInRange(self, minimum):
        return self.volume >= minimum