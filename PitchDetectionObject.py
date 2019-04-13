import pyaudio, aubio, numpy, os

class PitchDetectionObject(object):

    def __init__(self):
        # Opens pyaudio stream as callback and uses aubio to detect pitch
        # Handling of determined pitch found in helper checkNote
        self.pyaudioStreamFormat = pyaudio.paFloat32
        self.paChannels = 1
        self.sampleRate = 44100
        self.sampleSize = 1024
        self.tolerance = 0.8 #Tolerance for pitch detection


        self.p = pyaudio.PyAudio()


        self.openStream()

    def openStream(self):
        print("Opening callback stream...")
        self.stream = self.p.open(format=self.pyaudioStreamFormat,
            channels=self.paChannels,
            rate=self.sampleRate,
            input=True, output=False,
            frames_per_buffer=self.sampleSize,
            stream_callback=self.callback)

    def pitchDetectionInit(self):
        #Initialize pitch detection object
        pitchDetectionObject = aubio.pitch(hop_size=self.sampleSize)
        pitchDetectionObject.set_unit("midi")
        pitchDetectionObject.set_tolerance(self.tolerance)
        return pitchDetectionObject

    def callback(self, in_data, frame_count, time_info, status_flags):
        #Callback function for  pyAudio stream
        pitchDetectionObject = self.pitchDetectionInit()
        # Convert pyaudio data into array readable by aubio.
        # *** Not copied exactly, but made with reference to:
        # https://github.com/aubio/aubio/tree/master/python/
        #                                           demos/demo_pyaudio.py
        dataAubio = numpy.frombuffer(in_data, dtype=numpy.float32)
        # Get pitch as midi val by passing in data-returns list of one item
        pitchVal = pitchDetectionObject(dataAubio)[0]
        self.note = (aubio.midi2note(int(numpy.around(pitchVal))))
        # Convert Midi val to note
        return (in_data, pyaudio.paContinue)



    def closeStream(self):
        #closes stream
        print("Closing stream...")
        self.stream.close()

    def kill(self):
        # Terminates PyAudio instance
        self.p.terminate()
        self.note = None

    def getPitch(self):
        return self.note
