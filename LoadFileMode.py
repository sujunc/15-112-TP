import sys
import wave
from Pyaudio import *
from cmu_112_graphics import * #taken from course website
from SplashScreenMode import *
from tkinter import *
from PIL import Image
import math
from SplashScreenMode import *
print(f'{sys.executable} -m pip install pillow')
print(f'{sys.executable} -m pip install requests')

class LoadFileMode(Mode):
    def appStarted(mode):
        mode.buttonsMade=set()
        mode.loadingMusic=AudioFile("tetris.wav")
        mode.gameMusic=""
        mode.blankSlot=Button(mode.width/3, mode.height/2, mode.width*2/3, \
            mode.height/2+mode.height/6, "white", "rectangle",\
                 "Path to music file: ", mode.buttonsMade)
    def mousePressed(mode, event):
        for button in mode.buttonsMade:
            if button.shape=="rectangle":
                if button.x0<event.x<button.x1 and button.y0<event.y<button.y1:
                    if button==mode.blankSlot:
                        path=str(input()) #Question: Ask TA how.
                        if path!=None or path!="":
                            button.text+=path
                            mode.app.splashScreenMode.songLoaded=True
                    elif button==mode.loadButton:
                        mode.app.setActiveMode(mode.app.loadFileMode)
            elif button.shape=="oval":
                cx, cy=(x0+x1)/2, (y0+y1)/2
                if math.sqrt((event.x-cx)**2+(event.y-cy)**2):
                    button.color="Green"
    def redrawAll(mode, canvas):
        for button in mode.buttonsMade:
            button.drawButton(canvas)
