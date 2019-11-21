import sys
import wave
from Pyaudio import *
from cmu_112_graphics import * #taken from course website
from tkinter import *
from PIL import Image
import math
from SplashScreenMode import *
from GameMode import *
from LoadFileMode import *

class Run(ModalApp):
    def appStarted(app):
        app.splashScreenMode=SplashScreenMode()
        app.loadFileMode=LoadFileMode()
        app.gameMode=GameMode()
        app.setActiveMode(app.splashScreenMode)
app=Run(width=600, height=600)