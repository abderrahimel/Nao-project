
import time
import argparse
import math
import almath
import motion
from naoqi import ALBroker
from naoqi import ALProxy
from AutoMove import AvoidanceObstacle
IP = '192.168.3.68'
PORT = 9559

myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       IP,         # parent broker IP
       PORT)       # parent broker port

EviteObstacle = AvoidanceObstacle()
FRAME_TORSO = 0
FRAME_ROBOT = 2
currentCamera = "CameraBottom"
navigation = ALProxy("ALNavigation", IP, PORT)
navigation.setSecurityDistance(0.5) # set de security distance to 0.5
tts = ALProxy("ALTextToSpeech",IP, PORT)
motionProxy = ALProxy("ALMotion", IP, PORT)
tracker = ALProxy("ALTracker", IP, PORT)
posture = ALProxy("ALRobotPosture", IP, PORT)
memoryProxy = ALProxy("ALMemory", IP, PORT)
landmarkProxy = ALProxy("ALLandMarkDetection", IP, PORT)
video = ALProxy("ALVideoDevice", IP, PORT)
setcam = video.setActiveCamera(1) #Set bottom camera





def head(motionProxy): # set Head position that best sees the environment
    names = list()
    times = list()
    keys = list()

    names.append("HeadPitch")
    times.append([1.0])
    keys.append([math.radians(-14)])

    motionProxy.angleInterpolation(names, keys, times, True)


#landmark
def getMarkId():
    landmarkTheoreticalSize = 0.09  # LandMark size in meters
    # Subscribe to LandmarkDetected event from ALLandMarkDetection proxy.
    landmarkProxy.subscribe("landmarkTest")
    markId = None
    # Wait for a mark to be detected.
    markData = memoryProxy.getData("LandmarkDetected")
    if (markData is None or len(markData) == 0):
        markId = None
    else:
        markInfoArray = markData[1]
        for markInfo in markInfoArray:
            markShapeInfo = markInfo[0]
            markExtraInfo = markInfo[1]
            alpha = markShapeInfo[1]
            beta = markShapeInfo[2]
            print "mark  ID: %d" % (markExtraInfo[0])
            markId = markExtraInfo[0]

    return markId

def searchLandmark(motionProxy):
    motionProxy.setMoveArmsEnabled(False, False)
    while True:
       markId = getMarkId() #Check if any mark is seen
       if markId == None:
           print("searching.........")
           motionProxy.moveTo(0.0, 0.0, math.pi / 8) #If not, rotate robot 180/8 degrees
           time.sleep(2)
       else:
           break
    return markId

def headForward():
    """"""
    motionProxy = ALProxy("ALMotion")
    memoryProxy = ALProxy("ALMemory")
    # disable both arm left and right to control by the move task
    motionProxy.setMoveArmsEnabled(False, False)
    d = 0
    memoryProxy.insertData("FRI/d", d)
    motionProxy = ALProxy("ALMotion")
    # give the robot the ability to move his head from the left to right (HeadYaw)
    # and from the top to bottom (HeadPitch)
    names = ['HeadYaw', 'HeadPitch']
    times = [[0.5], [0.5]]
    motionProxy.angleInterpolation(names, [-d,0],times, True)

def find(x): #find specific mark X
    posture.goToPosture("StandInit", 1.0)
    head(motionProxy)
    #headForward()
    time.sleep(1)
    argu = x
    markId = None
    while True:
        markId = searchLandmark(motionProxy) #Find any mark
        if markId != argu: #If found mark is not X
            pass
        else:
            break
    print markId,"was found"
    return markId

def moveHead(x):
    """ move head to another angle [0 or pi/3 or pi/2 or 2pi/3 or pi] """
    d = x
    memoryProxy.insertData("FRI/d", d)
    names = ['HeadYaw', 'HeadPitch']
    times = [[0.5], [0.5]]
    motionProxy.angleInterpolation(names, [-d,0],times, True)

i = 0
headList = [1, 0.5, 0, -0.5, -1]


def goto(x): #Find and go to specific mark
    mark = x
    find(mark)
    landmarkTheoreticalSize = 0.09
    if mark % 2 == 1: #If mark is odd
        targetdistance = 0.5
    if mark % 2 == 0: #If mark is even
        targetdistance = 0.5
    targetName = "LandMark"
    tracker.registerTarget(targetName, [landmarkTheoreticalSize, [mark]])
    mode = "Move" #set move mode in mark tracking
    tracker.setMode(mode)
    tracker.track(targetName)
    too_far = True
    tracker.toggleSearch(False)
    while too_far:
        position = tracker.getTargetPosition(FRAME_ROBOT) #Get target distance to robot
        if position != []:
            #Trig to get distance
            distance = math.sqrt(math.pow(position[0],2) + math.pow(position[1],2))
            if distance < targetdistance:
                too_far = False
                theta = math.atan2(position[1], position[0])
                tracker.stopTracker()
                tracker.unregisterAllTargets()
                print distance
                print "Tracker: Target reached"
    too_far=True
    time.sleep(1.0)



def Block():

    # Choregraphe simplified export in Python.
    names = list()
    times = list()
    keys = list()

    names.append("HeadPitch")
    times.append([0.4, 2.16])
    keys.append([-0.167197, -0.167197])

    names.append("HeadYaw")
    times.append([0.4, 2.16])
    keys.append([0, 0])

    names.append("LAnklePitch")
    times.append([0.4, 2.16])
    keys.append([0.0885162, 0.0885162])

    names.append("LAnkleRoll")
    times.append([0.4, 2.16])
    keys.append([-0.127857, -0.127857])

    names.append("LElbowRoll")
    times.append([0.4, 2.16])
    keys.append([-0.414006, -0.414006])

    names.append("LElbowYaw")
    times.append([0.4, 2.16])
    keys.append([-1.18463, -1.18463])

    names.append("LHand")
    times.append([0.4, 2.16])
    keys.append([0.295054, 0.295054])

    names.append("LHipPitch")
    times.append([0.4, 2.16])
    keys.append([0.127857, 0.127857])

    names.append("LHipRoll")
    times.append([0.4, 2.16])
    keys.append([0.0983513, 0.0983513])

    names.append("LHipYawPitch")
    times.append([0.4, 2.16])
    keys.append([-0.167197, -0.167197])

    names.append("LKneePitch")
    times.append([0.4, 2.16])
    keys.append([-0.0885162, -0.0885162])

    names.append("LShoulderPitch")
    times.append([0.4, 2.16])
    keys.append([1.47235, 1.44221])

    names.append("LShoulderRoll")
    times.append([0.4, 2.16])
    keys.append([0.178406, 0.20943])

    names.append("LWristYaw")
    times.append([0.4, 2.16])
    keys.append([0.0962669, 0.0962669])

    names.append("RAnklePitch")
    times.append([0.4, 2.16])
    keys.append([0.0885162, 0.0885162])

    names.append("RAnkleRoll")
    times.append([0.4, 2.16])
    keys.append([0.127857, 0.127857])

    names.append("RElbowRoll")
    times.append([0.4, 2.16])
    keys.append([1.23395, 0.0349066])

    names.append("RElbowYaw")
    times.append([0.4, 2.16])
    keys.append([1.18463, 1.18498])

    names.append("RHand")
    times.append([0.4, 2.16])
    keys.append([1, 0.34])

    names.append("RHipPitch")
    times.append([0.4, 2.16])
    keys.append([0.127857, 0.127857])

    names.append("RHipRoll")
    times.append([0.4, 2.16])
    keys.append([-0.0983513, -0.0983513])

    names.append("RHipYawPitch")
    times.append([0.4, 2.16])
    keys.append([-0.167197, -0.167197])

    names.append("RKneePitch")
    times.append([0.4, 2.16])
    keys.append([-0.0885162, -0.0885162])

    names.append("RShoulderPitch")
    times.append([0.4, 2.16])
    keys.append([1.47235, 1.46867])

    names.append("RShoulderRoll")
    times.append([0.4, 2.16])
    keys.append([-0.178406, -0.196083])

    names.append("RWristYaw")
    times.append([0.4, 2.16])
    keys.append([0.0962669, 0.0962669])

    try:
        motionProxy = ALProxy("ALMotion")
        motionProxy.angleInterpolation(names, keys, times, True)
        tts.post.say("Voila la salle ")
    except BaseException, err:
        print err



def salle_x():
    goto(64)
    print("rotation pi/2")
    navigation.moveTo(0.0, 0.0, 1.57)
    #time.sleep(1)
    navigation.moveTo(1, 0.0, 0.0)
    #time.sleep(1)
    motionProxy.stopMove()
    navigation.moveTo(0.0, 0.0, -1.57)
    #time.sleep(1)
    navigation.moveTo(0.0, 0.0, 1.05)
    #time.sleep(1)
    navigation.moveTo(1, 0, 0)
    time.sleep(2)
    navigation.moveTo(0.0, 0.0, -1.57)
    time.sleep(1)
    navigation.moveTo(0.5, 0.0, 0.0)
    tts.say("voila la salle numero un ")
    

"""programme principale"""

#salle_x()