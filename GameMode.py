import sys
import wave
import pyaudio
from threading import *
from AubioBeatDetection import *
from cmu_112_graphics import * #Taken from course website
from tkinter import *
from PIL import Image
import math
print(f'{sys.executable} -m pip install pillow')
print(f'{sys.executable} -m pip install requests')

class GameMode(Mode):
    def appStarted(mode):
        mode.runImage=mode.loadImage("Running Sprite Sheet.png")
        mode.runSprites=mode.packSprite(mode.runImage,4)
        mode.duckImage=mode.loadImage("Ducking Sprite.png")
        mode.duckSprites=mode.packSprite(mode.duckImage, 1)
        mode.jumpImage=mode.loadImage("Jumping Sprite Sheet.png")
        mode.jumpSprites=mode.packSprite(mode.jumpImage, 2)
        mode.player=Player(0,0,20, mode.runSprites, mode.duckSprites,\
             mode.jumpSprites, mode)
        mode.runCounter=0
        mode.vanishingpoint=mode.height/3 #Arbitrary reference pt:2.5d graphics
        mode.gameOver=False
        mode.timer=0 #Tells how long to duck for
        mode.landBlocks=set()
        mode.musicLoaded=False
        mode.score=0
        mode.obstacles=set()
        if mode.app.gameMusic!="":
            mode.music=mode.app.gameMusic
            mode.musicLoaded=True
        else: mode.musicLoaded=False
        mode.beats=detectBeat(mode.music)
        mode.possibleObstacles=[]
        mode.tempo=mode.beats[1]-mode.beats[0]
        mode.vi=70
        mode.g=10
        mode.speed=15
        mode.i=1
        if mode.vi/mode.g>2:
            mode.i=int(mode.vi/mode.g*2)
        #Code commented out is a little buggy, 
        #for beat in range(0,len(mode.beats),mode.i): 
         #   if beat==0:
          #      landMass(-300,300,0,1000*mode.i+mode.beats[0]*mode.speed,\
           #         mode.landBlocks)
           # else: landMass(-300, 300, \
            #    1000*mode.i+mode.beats[beat-1]*mode.speed+\
             #       mode.tempo*mode.speed/(8*mode.i),\
              #  1000*mode.i+mode.beats[beat]*mode.speed, mode.landBlocks)
        landMass(-50,50,0, 500, mode.landBlocks) #For testing
        landMass(-50, 50, 515, 800, mode.landBlocks)
        landMass(50, 350, 700, 800, mode.landBlocks)
        landMass(-300, -100, 434, 623, mode.landBlocks)
    def generateTerrain(mode):
        pass
    def generateObstacles(mode):
        pass
    def packSprite(mode, image, frames):
        spriteList=[]
        width, height=image.size
        hr=220/height #Music Theory jokes
        scale=mode.scaleImage(image, hr) #Scales the image to be 220 pxls
        w, h=scale.size
        for i in range(frames):
            sprite=scale.crop((i*w/frames, 0, (i+1)*w/frames, h))
            spriteList+=[sprite] #Puts spritesheet into list
        return spriteList
    def keyPressed(mode, event):
        if mode.gameOver==False:
            if event.key=="Space":
                mode.player.jump(0, mode.g, mode.vi) #Does physics on player
            elif event.key=="a":
                mode.player.x-=5
                mode.player.apparentX-=5
                mode.player.renderX-=5
            elif event.key=="d":
                mode.player.x+=5
                mode.player.apparentX+=5
                mode.player.renderX+=5
            elif event.key=="s":
                mode.player.duck()
            elif event.key=="h":
                mode.player.turnLeft(mode)
            elif event.key=="l":
                mode.player.turnRight(mode)
    def clearObstacles(mode): #Checks if clears obstacles based on location, etc
        for obstacle in mode.obstacles:
            if (((obstacle.cx-obstacle.width/2<mode.player.x-\
                mode.player.width/2<\
                obstacle.cx+obstacle.width/2) or (obstacle.cx-obstacle.width/2\
                <mode.player.x+mode.player.width/2\
                    <obstacle.cx+obstacle.width/2))\
                     and \
                ((obstacle.cy-obstacle.depth/2<mode.player.y-\
                    mode.player.depth/2\
                <obstacle.cy+obstacle.depth/2) or (obstacle.cy-obstacle.depth/2\
                <mode.player.y+mode.player.depth/2<obstacle.cy+\
                    obstacle.depth/2)) and \
                ((obstacle.cz<mode.player.z-mode.player.height<\
                    obstacle.cz+obstacle.height) or \
                    (obstacle.cz<mode.player.z+mode.player.z\
                        <obstacle.cz+obstacle.height))):
                return obstacle
        return True
    def timerFired(mode):
        if mode.gameOver==False:
            mode.movePlayer() #Increments by steady run speed
            mode.score+=int(mode.speed/2) #Adds int score to player.
            mode.runCounter+=1 #Loops through sprite
            if mode.clearObstacles()!=True:
                mode.gameOver=True
            mode.passObstacles()
            if mode.musicLoaded==False:
                mode.musicLoaded==None
            if mode.player.z<= 20 and mode.isOnTop()==False: #Accounts for edge cs
                mode.player.supported=False
                mode.gameOver=True
            if mode.player.mode=="duck": 
                mode.timer+=1
                if mode.timer%20==0:
                    mode.player.mode="run"
                    mode.player.width, mode.player.height, mode.player.depth=\
                        mode.player.runWidth, mode.player.runHeight,\
                             mode.player.runDepth
            elif mode.player.mode=="jump":
                mode.player.upv-=mode.g
                mode.player.z+=mode.player.upv
                if mode.player.z<=20:
                    mode.player.mode="run"
            elif mode.player.z<20:
                #If the player's y falls inside the map's y, we know that 
                #the player is on solid ground, so we can change the is 
                #supported to True.
                if mode.isOnTop()!=False:
                    mode.player.supported=True
                    mode.player.mode="run"
                    mode.player.z=20
                    mode.player.upv=0
            else: 
                if mode.isOnTop()!=False:
                    mode.player.supported=True
                    mode.player.mode="run"
    def movePlayer(mode):
        if mode.player.dir==0:
            mode.player.y+=mode.speed
            mode.player.apparentY+=mode.speed
        elif mode.player.dir==1:
            mode.player.x-=mode.speed
            mode.player.apparentY+=mode.speed
        elif mode.player.dir==2:
            mode.player.y-=mode.speed
            mode.player.apparentY+=mode.speed
        elif mode.player.dir==3:
            mode.player.x+=mode.speed
            mode.player.apparentY+=mode.speed
    def passObstacles(mode):
        for obstacle in mode.obstacles:
            if obstacle.cleared==False:
                if mode.player.y>obstacle.cy+obstacle.depth:
                    obstacle.cleared=True
            
    def isOnTop(mode):
        for block in mode.landBlocks: #Checks if player is supported
            if block.onTop(mode):
                return block
        return False
    def redrawAll(mode, canvas):
        for i in range(0,40, 4): #Makes the background a gradiant
            canvas.create_rectangle(0,mode.height*i/40,mode.width,\
                 mode.height, fill="gray"+str(40-i), outline="gray"+str(40-i))
        for block in mode.landBlocks:
            block.draw(canvas, mode)
        if mode.gameOver==False:
            mode.orderedDrawing(canvas)
        else:
            pass
            #if mode.clearObstacles()!=True:
                #mode.player.drawDeathSequence(mode.clearObstacles(), mode)
            #elif mode.isOnTop==False:
                #mode.player.drawDeathSequence("fall")
        canvas.create_rectangle(0,0,mode.width/5,mode.height/8,fill="slategray")
    def orderedDrawing(mode, canvas): #Draws it differently if player passed
        if len(mode.obstacles)==0:
            mode.player.drawPlayer(mode, canvas)
        else:
            for obstacle in mode.obstacles:
                if obstacle.cleared==True:
                    mode.player.drawPlayer(mode, canvas)
                    obstacle.draw(canvas, mode)
                elif obstacle.cleared==False:
                    obstacle.draw(canvas,mode)
                    mode.player.drawPlayer(mode, canvas)
class Obstacles(object): #will have more subclasses later
    def __init__(self, cx, cy, cz, set, mode):
        self.cx=cx
        self.cy=cy
        self.cz=cz
        self.apparentcx=self.cx
        self.apparentcy=self.cy
        self.cleared=False
        self.type=None
        set.add(self)
    def __eq__(self, other):
        if isinstance(other, Obstacles):
            return ((self.cx==other.cx) and (self.cy==other.cy) and \
                (self.cz==self.cz) and (self.cleared==other.cleared)\
                     and self.type==other.type))
    def __hash(self):
        return hash(self.getHashables())
    def getHashables():
        return (self.cx, self.cy, self.cz, self.cleared, self.type)
    def draw(self, canvas, mode):
        vanishingpt=mode.vanishingpoint
        ratio=(mode.width/2)/(mode.height-vanishingpt)
        yMap=vanishingpt+(mode.height-120-vanishingpt)*(2/3)**\
            ((self.cy-mode.player.y)/100) #120 is coordintate of player
        image=self.frontImage.size ### change this line
        x, y=image
        scaleAtPoint=2*ratio*(yMap-vanishingpt)###change this later
        image=mode.scaleImage(self.image, scaleAtPoint/x)
        canvas.create_image(mode.width/2, yMap, \
            image=ImageTk.PhotoImage(image))
    
class LaserGrid(Obstacles): #Will work on this after image is drawn
    def __init__(self, cx, cy, cz, set, mode):
        super().__init__(cx, cy, cz, set, mode)
        image="LaserGrid.png"
        sideImage="laserGridSide.png"
        self.type="LaserGrid"
        self.frontImage=mode.loadImage(image)
        self.leftImage=mode.loadImage(sideImage)
        self.rightImage=mode.loadImage(sideImage)
        self.depth=5
        self.width=100
        self.height=75
class Spikes(Obstacles):
    def __init__(self, cx, cy, cz, set, mode):
        super().__init__(cx, cy, cz, set, mode)
        image="Spikes Front.png"
        leftImg="SpikesLeft.png"
        rightImg="SpikesRight.png"
        self.type="Spikes"
        self.frontImage=mode.loadImage(image)
        self.leftImage=mode.loadImage(leftImg)
        self.rightImage=mode.loadImage(rightImg)
        self.depth=3
        self.width=25
        self.height=25
class landMass(object):
    def __init__(self,x0, x1, y0, y1, set):
        self.x0=x0 #The true coordinates on a real map
        self.x1=x1 
        self.y0=y0
        self.y1=y1
        self.apparentX0=self.x0 #The "Apparent" coordinates, which is used for 
        self.apparentX1=self.x1 #drawing
        self.apparentY0=self.y0
        self.apparentY1=self.y1
        set.add(self)
    def __eq__(self, other):
        return isinstance(other, landMass) and self.x0==other.x0 and \
            self.x1==other.x1 and self.y0==other.y0 and self.y1==other.y1 
    def __hash__(self):
        return hash(self.getHashables())
    def getHashables(self):
        return (self.x0, self.x1, self.y0, self.y1)
    def onTop(self, mode):
        return (((self.y0<mode.player.y<self.y1) or \
                (self.y0>mode.player.y>self.y1)) and\
                     (self.x0<mode.player.x<self.x1))
    def draw(self, canvas, mode): #Draws Trapazoid
        #Takes each coordinate given (assumes that the terrain is rectangular)
        #and based on distance to the player, finds a point between the player 
        #and the vanishingpt to place the coordinate.Such a mapping is isometric
        vanishingpt=mode.vanishingpoint #As defined in appStarted
        ratio=(mode.width/2)/(mode.height-vanishingpt) 
        #^calculates 1/m, m being slope
        closeEdgeMap=vanishingpt+(mode.height-120-vanishingpt)*(2/3)**\
            ((self.apparentY0-mode.player.apparentY)/100) #120 is coordintate of player
        farEdgeMap=vanishingpt+(mode.height-120-vanishingpt)*(2/3)**\
            ((self.apparentY1-mode.player.apparentY)/100) #100 is random
        closeEdgeLeftMap=mode.width/2+ratio*(closeEdgeMap-vanishingpt)*\
            (self.apparentX0-mode.player.apparentX)/100
        closeEdgeRightMap=mode.width/2+ratio*(closeEdgeMap-vanishingpt)*\
            (self.apparentX1-mode.player.apparentX)/100
        farEdgeLeftMap=mode.width/2+ratio*(farEdgeMap-vanishingpt)*\
            (self.apparentX0-mode.player.apparentX)/100
        farEdgeRightMap=mode.width/2+ratio*(farEdgeMap-vanishingpt)*\
            (self.apparentX1-mode.player.apparentX)/100
        canvas.create_polygon(closeEdgeLeftMap, closeEdgeMap, \
        closeEdgeRightMap, closeEdgeMap, farEdgeRightMap,\
             farEdgeMap, farEdgeLeftMap, farEdgeMap, fill="gray")
        
class Player(object):
    def __init__(self,x,y,z,R,D,J, mode):
        self.x=x
        self.y=y
        self.z=z
        self.renderX=0
        self.apparentX=self.x
        self.apparentY=self.y
        self.dir=0
        self.runSprite=R
        self.duckSprite=D
        self.jumpSprite=J
        self.runWidth, self.runHeight, self.runDepth=\
            self.getRad(self.runSprite, mode) #Dimensions for player positions
        self.duckWidth, self.duckHeight, self.duckDepth=\
            self.getRad(self.duckSprite, mode)
        self.jumpWidth, self.jumpHeight, self.jumpDepth=\
            self.getRad(self.jumpSprite, mode)
        self.width,self.height, self.depth=\
            self.runWidth, self.runHeight, self.runDepth
        self.mode="run" #Modes are run, duck, and jump
        self.supported=True
        self.upv=0 #Current vertical velocity
    def turnLeft(self, mode):
        block=mode.isOnTop() #finds block player is on
        self.apparentX, self.apparentY=self.apparentY, -self.apparentX
        self.dir=(self.dir+1)%4
        for block in mode.landBlocks:
            block.apparentX0, block.apparentX1, block.apparentY0,\
            block.apparentY1=block.apparentY0, block.apparentY1,\
                    -block.apparentX0, -block.apparentX1
        #Note: This is linear algebra. Please recognize the amount of work \
        #I put into this
    def turnRight(self, mode): #works similiarly to turnLeft
        block=mode.isOnTop() 
        self.apparentX, self.apparentY=-self.apparentY, self.apparentX
        self.dir=(self.dir-1)%4
        for block in mode.landBlocks:
            block.apparentX0, block.apparentX1, block.apparentY0, \
            block.apparentY1=-block.apparentY1,-block.apparentY0,\
                block.apparentX0, block.apparentX1

    def jump(self, ground,g, vi): #Is basically just physics
        if self.supported==True: #If you are on a platform
            self.supported=False #You're leaving the platform
            self.mode="jump" 
            self.upv+=vi #adds upward velocity by initial velocity
            self.z+=self.upv #adds the velocity to vertical position
            self.width,self.height, self.depth=self.jumpWidth, self.jumpHeight,\
                 self.jumpDepth #reassign dimensions to jump sprite
    def duck(self): #Changes player dimensions 
        if self.mode!="duck":
            self.mode="duck"
            self.width,self.height, self.depth=self.duckWidth, self.duckHeight,\
                 self.duckDepth
    def getRad(self, L, mode): #Gets the dimensions of the sprite images
        if len(L)==0:
            return None
        else: #Returns the "radius" of player sprite
            width, height=L[0].size
            return width/2, height/2, height/4 
    def drawPlayer(self, mode, canvas):
        x,z=self.renderX, self.z
        #uses a different image for running, jumping, and ducking
        if self.mode=="run":
            canvas.create_image(mode.width/2+x,mode.height-z-100-55, \
            image=ImageTk.PhotoImage(mode.runSprites[mode.runCounter%4]))
        elif self.mode=="jump":
            canvas.create_image(mode.width/2+x, mode.height-z-100-55, \
                image=ImageTk.PhotoImage(mode.jumpSprites[mode.runCounter%2]))
        elif self.mode=="duck":
            canvas.create_image(mode.width/2+x, mode.height-z-100-55, \
                image=ImageTk.PhotoImage(mode.duckSprites[0]))
            #^Numbers: the canvas offset plus a quarter of the size of the image
    def drawDeathSequence(methodOfDeath, mode):
        if isinstance(methodOfDeath, str):
            pass
        elif isinstance(methodOfDeath, LaserGrid):
            image="LaserGridDeath.png"
            DeathByLaserGrid=mode.packSprite(image, 1)
            for frame in DeathByLaserGrid:
                canvas.create_image(mode.width/2+x,mode.height-z-100-55, \
                image=ImageTk.PhotoImage(frame))
        elif isinstance(methodOfDeath, Spike):
            pass

            

#class MyMusic(Thread): 
 #   def __init__(self, fileName):
  #      self.fileName=fileName
   #     self.waveform=wave.open(fileName)
    #    self.p=pyaudio.Pyaudio()
     #   self.stream=self.p.open()

