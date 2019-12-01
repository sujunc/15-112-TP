import wave
from Pyaudio import *
from cmu_112_graphics import * #taken from course website
from tkinter import *
from PIL import Image
import math
from GameMode import *
from SplashScreenMode import *

class GameOverMode(Mode):
    def appStarted(mode):
        mode.app.gameMode=GameMode()
    def keyPressed(mode, event):
        mode.app.gameMode=GameMode()
        if event.key=="Space":
            mode.app.setActiveMode(mode.app.gameMode)
        if event.key=="r":
            mode.app.setActiveMode(mode.app.splashScreenMode)
    def redrawAll(mode, canvas):
        if mode.app.gameWon==True:
            canvas.create_text(mode.width/2, mode.height/2, text="Superb!")
        else:
            canvas.create_text(mode.width/2, mode.height/2, text="A Nice Try",\
                font=f'Arial {int(mode.width/10)} bold')
        