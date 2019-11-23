import sys
import wave
from playsound import playsound
from cmu_112_graphics import * #Taken from course website
from tkinter import *
from PIL import Image
import math
print(f'{sys.executable} -m pip install pillow')
print(f'{sys.executable} -m pip install requests')

class GameMode(Mode):
    def appStarted(mode):
        mode.music=None #mode.app.loadFileMode.gameMusic
        #playsound(mode.music)
        mode.player=Player(0,0,20)
        mode.g=10
        mode.vanishingpoint=mode.height/3
        mode.gameOver=False
        mode.timer=0
        mode.landBlocks=set()
        #Arbitrary tester landMass
        mode.landMass1=landMass(-300, 300, 0, 300, mode.landBlocks)
        mode.landMass2=landMass(-300, 300, 305, 605, mode.landBlocks)
        mode.landMass3=landMass(-300, 300, 610, 910, mode.landBlocks)
    def keyPressed(mode, event):
        if mode.gameOver==False:
            if event.key=="Space":
                mode.player.jump(0, mode.g)
            elif event.key=="a":
                mode.player.x-=5
            elif event.key=="d":
                mode.player.x+=5
            elif event.key=="s":
                mode.player.duck()
    def timerFired(mode):
        if mode.gameOver==False:
            mode.player.y+=5
            print(mode.player.y)
            if mode.player.z<= 20 and not mode.isOnTop():
                mode.player.supported=False
                mode.gameOver=True
            if mode.player.ducking==True:
                mode.timer+=1
                if mode.timer%20==0:
                    mode.player.ducking=False
                    mode.player.z*=2
            elif mode.player.ducking==False:
                if mode.player.z>20:
                    mode.player.upv-=mode.g
                    mode.player.z+=mode.player.upv
                elif mode.player.z<20:
                    #If the player's y falls inside the map's y, we know that 
                    #the player is on solid ground, so we can change the is 
                    #supported to True.
                    if mode.isOnTop():
                        mode.player.supported=True
                        mode.player.z=20
                        mode.player.upv=0
                else: 
                    if mode.isOnTop():
                        mode.player.supported=True
    def isOnTop(mode):
        for block in mode.landBlocks: #Checks if player is supported
            if ((block.y0<mode.player.y<block.y1) or \
                (block.y0>mode.player.y>block.y1)) and\
                     (block.x0<mode.player.x<block.x1):
                return True
        return False
    def redrawAll(mode, canvas):
        for block in mode.landBlocks:
            block.draw(canvas, mode)
        x,z=mode.player.x, mode.player.z
        canvas.create_oval(mode.width/2-5+x,mode.height*5/6-5-z,\
            mode.width/2+5+x, mode.height*5/6+5-z)
class landMass(object):
    def __init__(self, x0,x1,y0, y1, set):
        self.x0=x0
        self.x1=x1
        self.y0=y0
        self.y1=y1
        set.add(self)
    def __eq__(self, other):
        return isinstance(other, landMass) and self.x0==other.x0 and \
            self.x1==other.x1 and self.y0==other.y0 and self.y1==other.y1
    def __hash__(self):
        return hash((self.x0, self.x1, self.y0, self.y1))
    def draw(self, canvas, mode):
        vanishingpt=mode.vanishingpoint
        ratio=(mode.width/2)/(mode.height-vanishingpt)
        leftCenterOffset=self.x0
        rightCenterOffset=self.x1
        closeEdgeMap=vanishingpt+(mode.height-120-vanishingpt)*(2/3)**\
            ((self.y0-mode.player.y)/100) #120 is coordintate of dot
        farEdgeMap=vanishingpt+(mode.height-120-vanishingpt)*(2/3)**\
            ((self.y1-mode.player.y)/100) #100 is random
        closeEdgeLeftMap=mode.width/2-ratio*(closeEdgeMap-vanishingpt)
        closeEdgeRightMap=mode.width/2+ratio*(closeEdgeMap-vanishingpt)
        farEdgeLeftMap=mode.width/2-ratio*(farEdgeMap-vanishingpt)
        farEdgeRightMap=mode.width/2+ratio*(farEdgeMap-vanishingpt)
        canvas.create_polygon(closeEdgeLeftMap, closeEdgeMap, \
        closeEdgeRightMap, closeEdgeMap, farEdgeRightMap,\
             farEdgeMap, farEdgeLeftMap, \
                 farEdgeMap, fill="gray")
class Player(object):
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
        self.supported=True
        self.upv=0
        self.ducking=False
    def jump(self, ground,g):
        if self.supported==True:
            self.supported=False
            self.upv+=50
            self.z+=self.upv
    def duck(self):
        if self.ducking==False:
            self.ducking=True
            self.z/=2 #Not quite finished debugging
