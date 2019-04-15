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
        self.note = ''


        self.p = pyaudio.PyAudio() #instantialize pyaudio

        self.openStream()

    def openStream(self):
        # Open pyaudio stream as callback
        print("Opening callback stream...")
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

        return (in_data, pyaudio.paContinue)



    def closeStream(self):
        #closes stream
        print("Closing stream...")
        self.stream.close()

    def kill(self):
        # Terminates PyAudio instance
        self.closeStream()
        self.p.terminate()
        self.note = ''

    def getNote(self):
        # Return midi value of current sung pitch
        return self.note

    def pitchInRange(self, lowerBound, upperBound):
        # Checks if current pitch is within a certain range of pitches
        # All as midiVals
        return lowerBound <= self.note <= upperBound