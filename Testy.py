import aubio
import numpy as np
import pyaudio
#Code taken from Panda3d manual
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3
import math
 
class MyApp(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)
        # Load the environment model.
        self.scene = self.loader.loadModel("models/environment")
        # Reparent the model to render.
        self.scene.reparentTo(self.render)
        # Apply scale and position transforms on the model.
        self.scene.setScale(0.25, 0.25, 0.25)
        self.scene.setPos(-8, 42, 0)
        #self.gates=self.load.loadModel('models/helix')
        #self.gates.setScale(1, 1, 1, )
        #self.scene.setPos(0,0,0)
        #self.gates.reparentTo(self.render)
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        self.pandaActor = Actor("models/panda-model",
                                {"walk": "models/panda-walk4"})
        self.pandaActor.setScale(0.005, 0.005, 0.005)
        self.pandaActor.reparentTo(self.render)
        # Loop its animation.
        self.pandaActor.loop("walk")
        pandaPosInterval1 = self.pandaActor.posInterval(13,
                                                        Point3(0, -10, 0),
                                                        startPos=Point3(0, 10, 0))
        pandaPosInterval2 = self.pandaActor.posInterval(13,
                                                        Point3(0, 10, 0),
                                                        startPos=Point3(0, -10, 0))
        pandaHprInterval1 = self.pandaActor.hprInterval(3,
                                                        Point3(180, 0, 0),
                                                        startHpr=Point3(0, 0, 0))
        pandaHprInterval2 = self.pandaActor.hprInterval(3,
                                                        Point3(0, 0, 0),
                                                        startHpr=Point3(180, 0, 0))
 
        # Create and play the sequence that coordinates the intervals.
        self.pandaPace = Sequence(pandaPosInterval1,
                                  pandaHprInterval1,
                                  pandaPosInterval2,
                                  pandaHprInterval2,
                                  name="pandaPace")
        self.pandaPace.loop()
 
 
    # Define a procedure to move the camera.
    #Code taken from Panda3d manual: 
    # https://www.panda3d.org/manual/?title=Controlling_the_Camera
    def spinCameraTask(self, task):
        angleDegrees = task.time * 10.0
        angleRadians = angleDegrees * (math.pi / 180.0)
        self.camera.setPos(20 * math.sin(angleRadians), -20.0 * \
            math.cos(angleRadians), 3)
        self.camera.setHpr(angleDegrees, 0, 0)
        return task.cont
 
app = MyApp()
app.run()