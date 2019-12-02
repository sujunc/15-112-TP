import wave
import pyaudio
from threading import *
from AubioBeatDetection import *
from cmu_112_graphics import * #Taken from course website
from tkinter import *
from PIL import Image
import math, random

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
        mode.deathCounter=0
        mode.vanishingpoint=mode.height/3 #Arbitrary reference pt:2.5d graphics
        mode.gameOver=False
        mode.app.gameWon=False
        mode.timer=0 #Tells how long to duck for
        mode.landBlocks=dict()
        mode.platformsCrossed=[]
        mode.musicLoaded=False
        mode.score=0
        mode.obstacles=dict()
        if mode.app.gameMusic!="":
            mode.music=mode.app.gameMusic
            mode.musicLoaded=True
        else: mode.musicLoaded=False
        mode.vi=70
        mode.g=10
        mode.speed=15
        mode.i=1
        mode.timeInAir=2*mode.vi/mode.g
        mode.unrefinedBeats=detectBeat(mode.music)
        mode.beats=mode.refineBeats(mode.unrefinedBeats)
        mode.generateTerrain()
    def generateTerrain(mode): #accounts for edge cases
        StartingBlock(-50, 50, 0, 300, mode.landBlocks, 0, mode.unrefinedBeats)
        landMass(-50, 50, 300, 500, mode.landBlocks, 1, mode.unrefinedBeats)
        if len(mode.beats)==0:
            EndingBlock(-50, 50, 350, 400, mode.landBlocks, 1, \
                mode.unrefinedBeats)
        elif len(mode.beats)==1:
            landMass(-50, 50, 350, 400, mode.landBlocks, 1, \
                mode.unrefinedBeats)
            EndingBlock(-50, 50, 450, mode.landBlocks, 2, mode.unrefinedBeats)
        else: 
            mode.generateMap()
            mode.generateEndPiece()
    def generateEndPiece(mode):
        key=len(mode.landBlocks)-1
        block=mode.landBlocks[key]
        width=abs(block.x1-block.x0)
        height=abs(block.y1-block.y0)
        olderKey=len(mode.landBlocks)-2
        olderBlock=mode.landBlocks[olderKey]
        x0, x1, y0, y1=olderBlock.x0, olderBlock.x1, olderBlock.y0,\
                olderBlock.y1
        if width<height: #if it is a straight block #1/3 is arbitrary
            if (y1<block.y1):
                mode.landBlocks[key+1]=EndingBlock(block.x0, block.x1, \
                    block.y1+1/2*mode.timeInAir*mode.speed, block.y1+\
                    10*mode.speed*5+1/2*mode.timeInAir\
                    *mode.speed, mode.landBlocks,key+1, mode.unrefinedBeats)
                    #mode.timeInAir*mode.speed=distance traveled while jumping
            elif (y1>block.y1):
                mode.app.gameMode=GameMode()
                mode.landBlocks[key+1]=EndingBlock(block.x0, block.x1, \
                    block.y0-1/2*mode.timeInAir*mode.speed-\
                        10*mode.speed*5, block.y0\
                    -1/2*mode.timeInAir*mode.speed, mode.landBlocks,key+1,\
                         mode.unrefinedBeats)
        elif width>height:
            if int(block.x0-x1)==0 or int((block.x0-105-x1)/10)==0:
                #105 being the safe distance when jumping
                mode.landBlocks[key+1]=EndingBlock(block.x1+\
                    (1/2)*mode.timeInAir*mode.speed, block.x1+\
                    10*mode.speed*5+\
                    (1/2)*mode.timeInAir*mode.speed, block.y0, block.y1, \
                    mode.landBlocks, key+1, mode.unrefinedBeats)
            elif int(block.x1-x0)==0 or int((block.x1+105-x0)/10)==0:
                mode.landBlocks[key+1]=EndingBlock(block.x0-10\
                    *mode.speed*5-(1/2)*mode.timeInAir*mode.speed,\
                        block.x0-(1/2)*mode.timeInAir*mode.speed, block.y0, \
                            block.y1, mode.landBlocks, key+1, mode.unrefinedBeats)
    def generateMap(mode):#You have a counter that keeps track of left and right
        #This way, it makes sure that the map never self intersects
        left=0
        right=0
        count=0 #makes sure that it is impossible to draw a left piece, \
        #a straight piece, and then immediate draw another left piece
        for beat in range(len(mode.beats)):
            num=random.randint(0, 3)
            if num==0: #Makes a piece that extends the path
                mode.generate0Map(beat)
                count+=1
            elif num==1: #Makes a piece that extends the path, but has a gap
                mode.generate1Map(beat)
                count+=1
            elif num==2: #makes a left piece
                if left<=right and count>1:
                    mode.generate2Map(beat) #makes a left piece
                    left+=1
                    count=0
                else:
                    mode.generate0Map(beat)
                    count+=1
            elif num==3: #makes a right piece
                if left>=right and count>1:
                    mode.generate3Map(beat) #makes right piece
                    right+=1
                    count=0
                else:
                    mode.generate1Map(beat) #makes gapped piece
                    count+=1
    def generate3Map(mode, beat):
        key=len(mode.landBlocks)-1
        block=mode.landBlocks[key]
        width=abs(block.x1-block.x0)
        height=abs(block.y1-block.y0)
        if beat==0:
            ref=0
        else: ref=mode.beats[beat-1]
        olderKey=len(mode.landBlocks)-2
        olderBlock=mode.landBlocks[olderKey]
        x0, x1, y0, y1=olderBlock.x0, olderBlock.x1, olderBlock.y0,\
            olderBlock.y1
        if width<height: #if it is a straight block
            if (y1<block.y1):
                mode.landBlocks[key+1]=landMass(block.x1, \
                block.x1+(mode.beats[beat]-ref)*mode.speed*5, block.y1-width, \
                    block.y1, mode.landBlocks, key+1, mode.unrefinedBeats)
        elif width>height: #if it is a sideways block
            if int(block.x0-x1)==0 or int((block.x0-105-x1)/10)==0:
                #105 being the safe distance when jumping
                mode.landBlocks[key+1]=landMass(block.x1-height, block.x1,\
                     block.y0-(mode.beats[beat]-ref)*mode.speed*5, block.y0, \
                    mode.landBlocks, key+1, mode.unrefinedBeats)
            elif int(block.x1-x0)==0 or int((block.x1+105-x0)/10)==0:
                mode.landBlocks[key+1]=landMass(block.x0, block.x0+height, \
                    block.y1, block.y1+(mode.beats[beat]-ref)*mode.speed*5, \
                        mode.landBlocks, key+1, mode.unrefinedBeats)
    def generate2Map(mode, beat):
        key=len(mode.landBlocks)-1
        block=mode.landBlocks[key]
        width=abs(block.x1-block.x0)
        height=abs(block.y1-block.y0)
        if beat==0:
            ref=0
        else: ref=mode.beats[beat-1]
        olderKey=len(mode.landBlocks)-2
        olderBlock=mode.landBlocks[olderKey]
        x0, x1, y0, y1=olderBlock.x0, olderBlock.x1, olderBlock.y0,\
                olderBlock.y1
        if width<height: #if it is a straight block
            if (y1<block.y1):
                mode.landBlocks[key+1]=landMass(block.x0-\
                (mode.beats[beat]-ref)*mode.speed*5, block.x0, block.y1-width, \
                    block.y1, mode.landBlocks, key+1, mode.unrefinedBeats)
        elif width>height:
            if int(block.x0-x1)==0 or int((block.x0-105-x1)/10)==0:
                #Eliminating floating point errors
                #105 being the safe distance when jumping
                mode.landBlocks[key+1]=landMass(block.x1-height, block.x1,\
                     block.y1, block.y1+(mode.beats[beat]-ref)*mode.speed*5, \
                    mode.landBlocks, key+1, mode.unrefinedBeats)
            elif int(block.x1-x0)==0 or int((block.x1+105-x0)/10)==0:
                mode.landBlocks[key+1]=landMass(block.x0, block.x0+height, \
                    block.y0-(mode.beats[beat]-ref)*mode.speed*5, block.y0, \
                        mode.landBlocks, key+1, mode.unrefinedBeats)
    def generate1Map(mode, beat):
        key=len(mode.landBlocks)-1
        block=mode.landBlocks[key]
        width=abs(block.x1-block.x0)
        height=abs(block.y1-block.y0)
        if beat==0:
            ref=0
        else: ref=mode.beats[beat-1]
        olderKey=len(mode.landBlocks)-2
        olderBlock=mode.landBlocks[olderKey]
        x0, x1, y0, y1=olderBlock.x0, olderBlock.x1, olderBlock.y0,\
                olderBlock.y1
        if width<height: #if it is a straight block #1/3 is arbitrary
            if (y1<block.y1):
                mode.landBlocks[key+1]=landMass(block.x0, block.x1, \
                    block.y1+1/2*mode.timeInAir*mode.speed, block.y1+\
                    (mode.beats[beat]-ref)*mode.speed*5+1/2*mode.timeInAir\
                    *mode.speed, mode.landBlocks,key+1, mode.unrefinedBeats)
                    #mode.timeInAir*mode.speed=distance traveled while jumping
        elif width>height:
            if int(block.x0-x1)==0 or int((block.x0-105-x1)/10)==0:
                #105 being the safe distance when jumping
                mode.landBlocks[key+1]=landMass(block.x1+\
                    (1/2)*mode.timeInAir*mode.speed, block.x1+\
                    (mode.beats[beat]-ref)*mode.speed*5+\
                    (1/2)*mode.timeInAir*mode.speed, block.y0, block.y1, \
                    mode.landBlocks, key+1, mode.unrefinedBeats)
            elif int(block.x1-x0)==0 or int((block.x1+105-x0)/10)==0:
                mode.landBlocks[key+1]=landMass(block.x0-(mode.beats[beat]-ref)\
                    *mode.speed*5-(1/2)*mode.timeInAir*mode.speed,\
                        block.x0-(1/2)*mode.timeInAir*mode.speed, block.y0, \
                            block.y1, mode.landBlocks, key+1, mode.unrefinedBeats)
    def generate0Map(mode, beat):
        key=len(mode.landBlocks)-1
        block=mode.landBlocks[key]
        width=abs(block.x1-block.x0)
        height=abs(block.y1-block.y0)
        if beat==0:
            ref=0
        else:
            ref=mode.beats[beat-1]
        olderKey=len(mode.landBlocks)-2
        olderBlock=mode.landBlocks[olderKey]
        x0, x1, y0, y1=olderBlock.x0, olderBlock.x1, olderBlock.y0,\
                olderBlock.y1
        if width<height: #if it is a straight block #1/3 is arbitrary
            if (y1<block.y1):
                mode.landBlocks[key+1]=landMass(block.x0, block.x1, \
                block.y1,block.y1+(mode.beats[beat]-ref)*mode.speed*5,\
                    mode.landBlocks,key+1, mode.unrefinedBeats)
        elif width>height:
            if int(block.x0-x1)==0 or int((block.x0-105-x1)/10)==0:
                mode.landBlocks[key+1]=landMass(block.x1, block.x1+\
                (mode.beats[beat]-ref)*mode.speed*5, block.y0, block.y1, \
                    mode.landBlocks, key+1, mode.unrefinedBeats)
            elif int(block.x1-x0)==0 or int((block.x1+105-x0)/10)==0:
                mode.landBlocks[key+1]=landMass(block.x0-(mode.beats[beat]-ref)\
                    *mode.speed*5,block.x0, block.y0, block.y1, \
                    mode.landBlocks, key+1, mode.unrefinedBeats)
    def generateObstacles(mode):
        #LaserGrid(0, 200, 0, mode.obstacles, mode)
        pass
    def refineBeats(mode, beats):
        lst=[]
        lst+=[beats[0]]
        lastBeat=0
        for beat in range(len(beats)):
            if beats[beat]-beats[lastBeat]>=mode.timeInAir*(3/20):
                lastBeat=beat #unit conversion
                lst+=[beats[beat]]
        return lst
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
                if mode.player.dir==0:
                    mode.player.x-=5
                elif mode.player.dir==1:
                    mode.player.y-=5
                elif mode.player.dir==2:
                    mode.player.x+=5
                elif mode.player.dir==3:
                    mode.player.y+=5
                mode.player.apparentX-=5
                mode.player.renderX-=5
            elif event.key=="d":
                if mode.player.dir==0:
                    mode.player.x+=5
                elif mode.player.dir==1:
                    mode.player.y+=5
                elif mode.player.dir==2:
                    mode.player.x-=5
                elif mode.player.dir==3:
                    mode.player.y-=5
                mode.player.apparentX+=5
                mode.player.renderX+=5
            elif event.key=="s":
                mode.player.duck()
            elif event.key=="h":
                mode.player.turnLeft(mode)
            elif event.key=="l":
                mode.player.turnRight(mode)
    def clearObstacles(mode): #Checks if clears obstacles based on location, etc
        if len(mode.obstacles)==0:
            return True
        for key in range(len(mode.obstacles)):
            obstacle=mode.obstacles[key]
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
                    mode.player.upv=0
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
        if mode.gameOver==True:
            mode.deathCounter+=1
            mode.app.setActiveMode(mode.app.gameOverMode)
    def movePlayer(mode):
        if mode.player.dir==0:
            mode.player.y+=mode.speed
            mode.player.apparentY+=mode.speed
        elif mode.player.dir==1:
            mode.player.x-=mode.speed#Since apparent X and Y are switched
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
                if mode.player.apparentY>obstacle.cy+obstacle.depth:
                    obstacle.cleared=True
    def isOnTop(mode):
        for key in range(len(mode.landBlocks)): #Checks if player is supported
            block=mode.landBlocks[key]
            if block.onTop(mode):
                if isinstance(block, EndingBlock):
                    mode.app.gameWon=True
                    return block
                if key==len(mode.platformsCrossed):
                    mode.turnOffInverse()
                    nextBlock=mode.landBlocks[key+1]
                    nextBlock.fill=nextBlock.inverse
                    mode.platformsCrossed+=[key]
                return block
        return False
    def turnOffInverse(mode):
        for key in range(len(mode.landBlocks)):
            if isinstance(mode.landBlocks[key], landMass) and not \
                isinstance(mode.landBlocks[key], StartingBlock) and not \
                isinstance(mode.landBlocks[key], EndingBlock):
                mode.landBlocks[key].fill=mode.landBlocks[key].color
    def redrawAll(mode, canvas):
        for i in range(0,40, 4): #Makes the background a gradiant
            canvas.create_rectangle(0,mode.height*i/40,mode.width,\
                 mode.height, fill="gray"+str(40-i), outline="gray"+str(40-i))
        for block in range(len(mode.landBlocks)):
            mode.landBlocks[block].draw(canvas, mode)
        if mode.gameOver==False:
            mode.orderedDrawing(canvas)
        else:
            if mode.clearObstacles()!=True:
                mode.player.drawDeathSequence(canvas, mode.clearObstacles(),\
                     mode, mode.deathCounter)
            elif mode.isOnTop()==False:
                mode.player.drawDeathSequence(canvas, "fall", mode,\
                     mode.deathCounter)
        canvas.create_rectangle(0,0,mode.width/5,mode.height/8,fill="slategray")
        canvas.create_text(mode.width/10, mode.height/16, fill="white", text=\
            f"{mode.score}")
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
                     and (self.type==other.type))
    def __hash__(self):
        return hash(self.getHashables())
    def getHashables(self):
        return (self.cx, self.cy, self.cz, self.cleared, self.type)
    def draw(self, canvas, mode):
        vanishingpt=mode.vanishingpoint
        ratio=(mode.width/2)/(mode.height-vanishingpt)
        yMap=vanishingpt+(mode.height-120-vanishingpt)*(2/3)**\
            ((self.cy-mode.player.y)/100) #120 is coordintate of player
        image=self.frontImage.size ### change this line
        x, y=image
        scaleAtPoint=2*ratio*(yMap-vanishingpt)###change this later
        image=mode.scaleImage(self.frontImage, scaleAtPoint/x)
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
        self.depth=10
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
    def __init__(self,x0, x1, y0, y1, dict, key, beats):
        self.x0=x0 #The true coordinates on a real map
        self.x1=x1 
        self.y0=y0
        self.y1=y1
        self.key=key
        self.beats=beats
        self.apparentX0=self.x0 #The "Apparent" coordinates, which is used for 
        self.apparentX1=self.x1 #drawing
        self.apparentY0=self.y0
        self.apparentY1=self.y1
        self.beats=beats
        if len(self.beats)==0: self.tempo=0
        else: #tempo as measured by beats per minute
            self.tempo=60*len(self.beats)/(self.beats[-1]) 
            #print(self.beats)
        if self.tempo==0:
            self.color="gray"
            self.inverse="black"
        elif 40>self.tempo:
            self.color="brown"
            self.inverse="gray"
        elif self.tempo>208:
            self.color="slategray"
            self.inverse="blue"
        elif 40<=self.tempo<=50:
            self.color="pink"
            self.inverse="light green"
        elif 50<self.tempo<=60:
            self.color="peach puff"
            self.inverse="light blue"
        elif 60<self.tempo<=72:
            self.color="light yellow"
            self.inverse="cyan"
        elif 72<self.tempo<80:
            self.color="light green"
            self.inverse="pink"
        elif 80<=self.tempo<120:
            self.color="light blue"
            self.inverse="peach puff"
        elif 120<=self.tempo<160:
            self.color="plum"
            self.inverse="aquamarine"
        else:
            self.color="lavender"
            self.inverse="palegreen"
        self.fill=self.color
        dict[key]=self
    def __eq__(self, other):
        return isinstance(other, landMass) and self.x0==other.x0 and \
            self.x1==other.x1 and self.y0==other.y0 and self.y1==other.y1 and \
                self.key==other.key
    def __hash__(self):
        return hash(self.getHashables())
    def getHashables(self):
        return (self.x0, self.x1, self.y0, self.y1, self.key)
    def onTop(self, mode):
        return (((self.y0<=mode.player.y<=self.y1) or \
                (self.y0>=mode.player.y>=self.y1)) and\
                     (self.x0<=mode.player.x<=self.x1))
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
             farEdgeMap, farEdgeLeftMap, farEdgeMap, fill=self.fill)
class StartingBlock(landMass):
    def __init__(self,x0, x1, y0, y1, dict, key, beats):
        super().__init__(x0, x1, y0, y1, dict, key, beats)
        self.color="gray"
class EndingBlock(landMass):
    def __init__(self,x0, x1, y0, y1, dict, key, beats):
        super().__init__(x0, x1, y0, y1, dict, key, beats)
        if len(self.beats)==0:
            self.tempo=0
        else: #tempo as measured by beats per minute
            self.tempo=60*len(self.beats)/self.beats[-1] 
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
        deathFallImage=mode.loadImage("Falling to your Death.png")
        self.fallDeath=mode.packSprite(deathFallImage, 5)
        laserGridDeath=mode.loadImage("LaserGridDeath.png")
        self.laserGridDeath=mode.packSprite(laserGridDeath, 1)
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
        for key in range(len(mode.landBlocks)):
            block=mode.landBlocks[key]
            block.apparentX0, block.apparentX1, block.apparentY0,\
            block.apparentY1=block.apparentY0, block.apparentY1,\
                    -block.apparentX0, -block.apparentX1
        #Note: This is linear algebra. Please recognize the amount of work \
        #I put into this
    def turnRight(self, mode): #works similiarly to turnLeft
        block=mode.isOnTop() 
        self.apparentX, self.apparentY=-self.apparentY, self.apparentX
        self.dir=(self.dir-1)%4
        for key in range(len(mode.landBlocks)):
            block=mode.landBlocks[key]
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
            canvas.create_image(mode.width/2+x,mode.height-z-100-110, \
            image=ImageTk.PhotoImage(mode.runSprites[mode.runCounter%4]))
        elif self.mode=="jump":
            canvas.create_image(mode.width/2+x, mode.height-z-100-110, \
                image=ImageTk.PhotoImage(mode.jumpSprites[mode.runCounter%2]))
        elif self.mode=="duck":
            canvas.create_image(mode.width/2+x, mode.height-z-100-110, \
                image=ImageTk.PhotoImage(mode.duckSprites[0]))
            #^Numbers: the canvas offset plus a quarter of the size of the image
    def drawDeathSequence(self, canvas, methodOfDeath, mode, counter):
        x,z=self.renderX, self.z
        if isinstance(methodOfDeath, str):
            if methodOfDeath=="fall":
                if counter<5:
                    canvas.create_image(mode.width/2+x,mode.height-z-100-110, \
                        image=ImageTk.PhotoImage(self.fallDeath[counter]))
        elif isinstance(methodOfDeath, LaserGrid):
            canvas.create_image(mode.width/2+x,mode.height-z-100-110, \
                image=ImageTk.PhotoImage(self.laserGridDeath[0]))
        elif isinstance(methodOfDeath, Spike):
            canvas.create_image(mode.width/2+x,mode.height-z-100-110, \
             image=ImageTk.PhotoImage(self.duckSprite[0])) #Cutting corners

            

#class MyMusic(Thread): 
 #   def __init__(self, fileName):
  #      self.fileName=fileName
   #     self.waveform=wave.open(fileName)
    #    self.p=pyaudio.Pyaudio()
     #   self.stream=self.p.open()

