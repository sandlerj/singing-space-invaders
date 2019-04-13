## This should all get turned into an object

import pyaudio, aubio, numpy
import os

if __name__ == "__main__":
    #sets up data struct incase this file is being used stand alone
    class Struct():pass
    data=Struct()

def pitchDetectionInit():
    #Initialize pitch detection object
    sampleSize = 1024
    pitchDetectionObject = aubio.pitch(hop_size=sampleSize)
    pitchDetectionObject.set_unit("midi")
    tolerance = 0.8 #Tolerance for pitch detection
    pitchDetectionObject.set_tolerance(tolerance)
    return pitchDetectionObject



def checkNote(note, data):
    if note not in data.notes:
        print(note)
        data.notes.add(note)


def noteDetectionStream(data): 
    # Opens pyaudio stream as callback and uses aubio to detect pitch
    # Handling of determined pitch found in helper checkNote
    pyaudioStreamFormat = pyaudio.paFloat32
    paChannels = 1
    sampleRate = 44100
    sampleSize = 1024

    data.p = pyaudio.PyAudio()


    data.notes = set()

    def callback(in_data, frame_count, time_info, status_flags):
        #Callback function for  pyAudio stream
        pitchDetectionObject = pitchDetectionInit()
        # Convert pyaudio data into array readable by aubio.
        # *** Not copied exactly, but made with reference to:
        # https://github.com/aubio/aubio/tree/master/python/demos/demo_pyaudio.py
        dataAubio = numpy.frombuffer(in_data, dtype=numpy.float32)
        # Get pitch as midi val by passing in data (returns list of one item)
        pitchVal = pitchDetectionObject(dataAubio)[0]
        note = (aubio.midi2note(int(numpy.around(pitchVal))))
        # Convert Midi val to note
        checkNote(note, data)
        return (in_data, pyaudio.paContinue)
    print("Opening callback stream...")
    data.stream = data.p.open(format=pyaudioStreamFormat,
        channels=paChannels,
        rate=sampleRate,
        input=True, output=True,
        frames_per_buffer=sampleSize,
        stream_callback=callback)

def closeStream(data):
    #closes stream
    print("Closing stream...")
    data.stream.close()
    data.p.terminate()
