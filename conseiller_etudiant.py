# -*- encoding: UTF-8 -*-
import os
import sys
import time
from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
from AutoMove import AvoidanceObstacle
from  salle import *
#from markerTrack import
Adviser = None
memory = None

class AdviserModule(ALModule):
    """ A simple module able to react
    to facedetection events

    """
    def __init__(self, name):
        ALModule.__init__(self, name)

        self.name = name
        self.tts = ALProxy("ALTextToSpeech")
        self.motion = ALProxy("ALMotion")
        self.memory = ALProxy("ALMemory")
        self.dialog = ALProxy("ALDialog")
        self.dialog.setLanguage("French")
        self.navigation = ALProxy("ALNavigation")
        self.navigation.setSecurityDistance(0.5)
        self.EviteObstacle = AvoidanceObstacle()
        self.lookForEtudiant()

    def lookForEtudiant(self):
        self.memory.subscribeToEvent("FaceDetected",self.name,"onFaceDetected")
       self.EviteObstacle.run()
       #self.navigation.moveTo(0.05, 0.0, 0.0)

    def onFaceDetected(self, *_args):

        # unsubscribe To Event FaceDetected
        self.memory.unsubscribeToEvent("FaceDetected",self.name)

        self.EviteObstacle.runFlage(False) # stop moving
        self.tts.say("salut")
        # subscribe to the event stop in memory
        #self.motion.stopMove()
        self.memory.subscribeToEvent("stop", self.name, "exitDialog")
       #self.nameTopic = os.path.abspath("dialog_frf.top")
        self.topic = self.dialog.loadTopic("/home/nao/dialog_frf.top") #/home/nao/dialog_frf.top
        # subscribe to the module
        self.dialog.subscribe(self.name)
        self.dialog.activateTopic(self.topic)
        self.memory.subscribeToEvent("consigne", self.name, "onconsigne")

    def onconsigne(self, *_args):
        #self.memory.unsubscribeToEvent("FaceDetected",self.name)
        self.memory.unsubscribeToEvent("consigne", self.name)
        marker = self.memory.getData("consigne")
        salle_x()


    def exitDialog(self, *_args):
        self.memory.unsubscribeToEvent("stop", self.name)

        self.dialog.deactivateTopic(self.topic)
        self.dialog.unloadTopic(self.topic)
        self.dialog.unsubscribe(self.name)
        # detect obstacle
        # self.EviteObstacle.obstacleCheck()
        # evite obstacle
        #self.EviteObstacle.eviteObstacle_v()
        self.lookForEtudiant() # trying to find anothor human


    def shutoff(self):

        try:
            self.dialog.deactivateTopic(self.topic)
            self.dialog.unloadTopic(self.topic)
            self.dialog.unsubscribe(self.name)
            print "stopped dialog"
        except RuntimeError:
            pass
        try:
            self.motion.stopMove()
            print "unsubscribed to face and stopped walk"
        except RuntimeError:
            pass

def main():

    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       '192.168.3.68',         # parent broker IP
       9559)       # parent broker port

    # Warning: Adviser must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global Adviser
    Adviser = AdviserModule("Adviser")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        Adviser.shutoff() # stop the module
        myBroker.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()