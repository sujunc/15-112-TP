import sys
import wave
from Pyaudio import *
from cmu_112_graphics import * #taken from course website
from tkinter import *
from PIL import Image
import math
print(f'{sys.executable} -m pip install pillow')
print(f'{sys.executable} -m pip install requests')

class SplashScreenMode(Mode):
    def appStarted(mode):
        mode.buttonsMade=set()
        mode.songLoaded=True #Change to False when implmenting actual game
        mode.song=AudioFile("Tuning Note A.wav") 
        #Below vals are arbitrary
        mode.loadButton=Button(mode.width/6, mode.height*2/3, mode.width*5/6, \
            mode.height*5/6, "gray", "rectangle", "Load Song", mode.buttonsMade)
        mode.startButton=Button(mode.width/6, mode.height/2, mode.width*5/6, \
            mode.height*2/3, "gray", "rectangle", "Start the Game!",\
                mode.buttonsMade)
        mode.colorDict={0:"pink", 1:"peach puff", 2:"light yellow",\
            3:'light green', 4:'light blue', 5: 'plum' ,6:'lavender'}
        mode.colorCont=0
    def mousePressed(mode, event):
        for button in mode.buttonsMade:
            if button.shape=="rectangle":
                if button.x0<event.x<button.x1 and button.y0<event.y<button.y1:
                    if button==mode.startButton and mode.songLoaded:
                        mode.app.setActiveMode(mode.app.gameMode)
                    elif button==mode.loadButton:
                        mode.app.setActiveMode(mode.app.loadFileMode)
            elif button.shape=="oval":
                cx, cy=(x0+x1)/2, (y0+y1)/2
                if math.sqrt((event.x-cx)**2+(event.y-cy)**2):
                    button.color="Green"
    def timerFired(mode):
        mode.colorCont+=1
    def redrawAll(mode, canvas):
        color=mode.colorDict[mode.colorCont%7] #7 for colors of the rainbow
        canvas.create_rectangle(0,0, mode.width, mode.height, fill=color)
        #Aribtrary numbers
        canvas.create_text(mode.width/2, mode.height/3, text="Music Run", \
            font=f'Times {mode.width//10}', fill='white')
        for button in mode.buttonsMade:
            button.drawButton(canvas)
class Button(object):
    def __init__(self, x0, y0, x1, y1, color, shape, text, set):
        self.x0=x0
        self.y0=y0
        self.x1=x1
        self.y1=y1
        self.color=color
        self.shape=shape
        self.text=text
        set.add(self)
    def drawButton(self, canvas):
        if self.shape=="rectangle":
            canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1, \
                fill=self.color)
        elif self.shape=="oval":
            canvas.create_oval(self.x0, self.y0, self.x1, self.y1,\
                 fill=self.color)
        if self.text!=None: #Find center
            canvas.create_text((self.x0+self.x1)/2, (self.y0+self.y1)/2,\
                 text=self.text)
    def __eq__(self, other):
        return isinstance(other,Button) and (self.x0==other.x0) and\
            (self.y0==other.y0) and (self.x1==other.x1) and (self.y1==other.y1)\
                and (self.shape==other.shape)
    def __hash__(self):
        return hash((self.x0, self.y0, self.x1, self.y1, self.shape, self.text))

