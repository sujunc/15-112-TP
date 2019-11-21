import aubio
import pyaudio
import numpy as np
import sys, os


#Modified from https://git.aubio.org/?p=aubio.git;a=blob;f=python/
# demos/demo_pitch.py;h=81f17cd4b3eed408abb31adbccd1ba39296dbacd;hb=
# c3c6305987848593034cb34501a9d3bc7afd6e8c
#Parses in downsample and tolerance
def detect(filename):
        downsample=8
        tolerance=0.8
        samplerate = 44100 // downsample
        win_s = 4096 // downsample # fft size
        hop_s = 512  // downsample # hop size
        s = aubio.source(filename, samplerate, hop_s)
        samplerate = s.samplerate
        pitch_o = aubio.pitch("yinfft", win_s, hop_s, samplerate)#Algorithm type
        pitch_o.set_unit("freq")
        pitch_o.set_tolerance(tolerance)
        pitches = []
        confidences = []
        # total number of frames read
        total_frames = 0
        counter = 0
        while True:
            samples, read = s()
            pitch = pitch_o(samples)[0]
            confidence = pitch_o.get_confidence()
            print (f"{total_frames/float(samplerate)} {pitch} {confidence}")
            print(pitch, guess(pitch))
            pitches += [pitch]
            confidences += [confidence]
            total_frames += read
            if read < hop_s: break
        letterList = []
        newPitches = []
        for index in range(0, len(pitches), len(pitches)//20):
            totalFreq = 0
            if(index+5 <= len(pitches)):
                for freq in range(index, index+5):
                    totalFreq += pitches[freq]
                averageFreq = totalFreq/5
                newPitches.append(averageFreq)
            else:
                counter = 0
                for index in range(index, len(pitches)):
                    totalFreq += pitches[freq]
                    counter += 1
                averageFreq = totalFreq/counter
                newPitches.append(averageFreq)
        for pi in newPitches:
            letterName = guess(pi)
            letterList.append(letterName)
        newList = modifyList(letterList)
        note = findModeInList(newList)
        return letterList
def findModeInList(newList):
    d=dict()
    for note in newList:
        if note not in d:
            d[note]=1
        else: d[note]+=1
    return 
def modifyList(letterList):
    pitchOrderedList=[]
    for i in range(len(letterList)):
        if len(pitchOrderedList)==0:
            pitchOrderedList+=[letterList[i]]
        elif letterList[i] !=pitchOrderedList[-1]:
            pitchOrderedList+=[letterList[i]]
    return pitchOrderedList
        

#Modified from Aubio demo from TA led lecture. https://docs.google.com/
# document/d/192wuR7T5np9-tB1YIkh3QzrvtmRovcjjeZBqZKS2kwU/edit
def guess(frequency):
    maxDif = 10000000
    note = None
    pitchDictionary = {"E2": 82.41, "F2": 87.31, "Gb2" : 92.50, "G2": 98.00,
        "Ab2": 103.83, "A2": 110.00, "Bb2": 116.54, "B2": 123.47, "C3": 130.81, 
        "Db3": 138.59, "D3": 146.83, "Eb3": 155.56, "E3": 164.81, "F3": 174.61, 
        "Gb3": 185.00, "G3": 196.00, "Ab3": 207.65, "A3": 220.00, "Bb3": 233.08, 
        "B3": 246.94, "C4": 261.63, "Db4": 277.18, "D4": 293.66, "Eb4": 311.13, 
        "E4": 329.63, "F4": 349.23, "Gb4": 369.99, "G4": 392.00, "Ab4": 415.30,
        "A4": 440.00, "Bb4": 466.16, "B4": 493.88, "C5": 523.25, "Db5": 554.37,
        "D5": 587.33, "Eb5": 622.25, "E5": 659.25, "F5": 698.46, "Gb5": 739.99,
        "G5": 783.99, "Ab5": 830.61, "A5": 880.00, "Bb5": 932.33, "B5": 987.77, 
        "C6": 1046.50 }
    for key in pitchDictionary:
        dif = abs(pitchDictionary[key] - frequency)
        if(dif < maxDif):
            maxDif = dif
            note = key
    return note

#Taken from https://docs.google.com/document/d/192wuR7T5np9-tB1YIkh3QzrvtmRovcjj
# eZBqZKS2kwU/edit
def buildChords(note, chordType, inversion):
    if(note != []):
        note = note[0]
        noteOrder = ["E2","F2", "Gb2", "G2",
            "Ab2", "A2", "Bb2", "B2", "C3", 
             "Db3", "D3", "Eb3", "E3", "F3", 
            "Gb3", "G3", "Ab3","A3", "Bb3", 
            "B3", "C4",  "Db4",  "D4", "Eb4",
            "E4", "F4", "Gb4", "G4", "Ab4",
            "A4", "Bb4", "B4", "C5", "Db5",
            "D5", "Eb5", "E5", "F5", "Gb5",
            "G5","Ab5", "A5", "Bb5", "B5",
            "C6", "Db6", "D6", "Eb6", "E6", 
            "F6", "Gb5", "G5"]
        indexOfRoot = noteOrder.index(note)
        root = noteOrder[indexOfRoot]
        if(chordType == "Major"):
            majorThird = 4
            m3 = noteOrder[indexOfRoot + majorThird]
            third = m3
        elif(chordType == "Minor"):
            minorThird = 3
            m3 = noteOrder[indexOfRoot + minorThird]
            third = m3
        perfectFifth = 7
        p5 = noteOrder[indexOfRoot + perfectFifth]
        octave = 12
        fifth = p5
        if(inversion == 1):
            root = m3
            third = p5
            fifth = noteOrder[indexOfRoot + octave]
        if(inversion == 2):
            indexOfFifth = noteOrder.index(p5)
            root = noteOrder[indexOfFifth-octave]
            third = noteOrder[indexOfRoot]
            indexOfThird = noteOrder.index(m3)
            fifth = noteOrder[indexOfThird]
        chord = [root, third, fifth]
        return chord

print(detect("Twinkle.wav"))