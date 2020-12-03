import math
import sys
import time
import almath			# angle to rad
import argparse			
import threading    	
from naoqi import ALProxy
from naoqi import ALBroker


class AvoidanceObstacle(threading.Thread):

    def __init__(self):
        """ initialisation """
        threading.Thread.__init__(self)
        # initiation attribute the class of thread
        self.angleTurn = 180 # angle de rotation unite angle
        self.moveSpeed = 0.4 #speed movement m/s
        self.delaySeconds = 0.3 #set delay event unit second
        self.checkDistance = 0.5 #distance of securite
        self.obstacleLeft = False #True obstacle lift
        self.obstacleRight = False #True obstacle right
        self.obstacleFront = False # True obstacle front
        self.runFlage = False  # flag for stoping the robot to move
        self.obstacle = False 
        self.motion = ALProxy("ALMotion")
        
        self.memory =ALProxy("ALMemory")
        self.sonar = ALProxy("ALSonar")
        self.navigation = ALProxy("ALNavigation")
        self.navigation.setSecurityDistance(0.5) # set de security distance to 0.5
        print("starting")        

    def getFlag(self):
        """ return the FLAG with type boolean,True :  running
           False : stop move
        """
        return self.runFlage
 
    def setFlag(self, bools):
        """ set to run FLAG to control the on/off of moving"""
        #of obstacle avoidance function
        self.runFlage = bools
        return self.runFlage

    def run(self):
        """
        detecte if the obstacle into the cone and deteremine 
        the direction to march robot with fonction obstacle signal

        stop with self.runFlage = False
        """
        # definie self.runFlage  to True
        self.setFlag(True)
        # start robot
        self.motion.wakeUp()
        self.motion.moveInit()
        # subscribe to ultrasound
        self.sonar.subscribe("ClassAvoidanceObstacle")
        while self.runFlage:#obstacle avoidance flag is True, continuons loop detection
            # 1. detect obstacle
            self.obstacleCheck()
            # 2.determinie the walking direction according to the obstacle
            #self.eviteObstacle()
            self.eviteObstacle_v() 
            # 3. delay
            time.sleep(self.delaySeconds)

        # until self.runFlag is False,the while loop will not jump out
        #unsubscribe from ultrasound
        self.sonar.unsubscribe("ClassAvoidanceObstacle")
        # robot reset
        self.motion.stopMove()

    def stop(self):
        """change the flag to False to stoping the robot """
        self.setFlag(False)

    def obstacleCheck(self):
        """check obstacle"""
        # detect ultrasonic value and set flag
        leftValue = self.memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")
        rightValue = self.memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")
        # this is method ruturn 1 if obstacle front
        # 
        dist = self.navigation.moveTo(self.moveSpeed, 0, 0) 
        # distance sensor 
        #    <-------------0.5m-------------->self.checkDistance
        #    <----------------> Value sensor
        # check obstacle left

        if leftValue > self.checkDistance: # obstacle far with robot in left

            self.obstacleLeft = False
        else: # less than securite distance,there are obstacles
            self.obstacleLeft = True
        # check obstacle right
        if rightValue > self.checkDistance: # obstacle far with robot in right
            self.obstacleRight = False
 
        else:
            self.obstacleRight = True
        
        if dist:
            self.obstacleFront = True
        else:
            self.obstacleFront = False 

    def eviteObstacle(self):
        #        left             right          Front               avoid
        
        #        False            False                              no obstacle turn Right
        #        False            True                               obstacle right turn left
        #        True             False                              obstacle left  turn right
        #        True             True                               obstacle left and right turn ...
        if not self.obstacleLeft:
            if not self.obstacleRight:
                self.moveGo()
            else:
                self.turnLeft()
        else:
            if not self.obstacleRight:
                self.turnRight()
            else:
                self.backTo()

    def eviteObstacle_v(self):
        """evite obstacles"""
         #      left                 right               front         Go            self.Forward()
         #       F                    F                    F             self.turnRight() or self.turnLeft()
         #       F                    F                    T            L or R
         #       F                    T                    F            L or front
         #       F                    T                    T            L
         #       T                    F                    F            R or Front
         #       T                    F                    T            R
         #       T                    T                    F            Front
         #       T                    T                    T            self.Obstacle_L_R_F()
        if not self.obstacleLeft:

            if not self.obstacleRight:

                if not self.obstacleFront:
                    self.stopAndTurnAngle() #self.turnRight() self.Forward()
                else:
                    self.turnRight()
            else:
                if not self.obstacleFront:

                    self.stopAndTurnAngle()
                else:
                    self.turnLeft()
        else:

            if not self.obstacleRight:

                if not self.obstacleFront:

                    self.stopAndTurnAngle()
                else:

                    self.turnRight()
            else:

                if not self.obstacleFront:

                    self.stopAndTurnAngle()
                else:

                    self.Obstacle_L_R_F()

 

    def eviteObstacle_v0(self):
        """
        (i) call navigationProxy.moveTo()
        (ii) if there exit obstacle the robot stop and turn to a certain angle .Assume the security distance is 0.3 m
        between the robot and the obstacle
        else walks forward

        """
        self.call = self.navigation.moveTo(self.moveSpeed, 0, 0)
        if self.call:
            
            self.stopAndTurnAngle()
        else:
            self.motion.moveTo(self.moveSpeed,0,0)

    def moveGo(self):
        """move == forward"""
        self.motion.move(self.moveSpeed, 0, 0)

    def Forward(self):
        """forward"""
        self.motion.moveTo(self.moveSpeed, 0, 0)


    def stopAndTurnAngle(self):
        """stop and turn right"""
        self.angle = -1.0 *self.angleTurn * almath.TO_RAD 
        self.StopMove()       #stop
        self.motion.moveTo(0, 0, self.angle) #self.navigation.moveTo(0, 0, self.angle)# turn angle

    def StopMove(self):  #Methode to stop moving
        """stop"""
        self.motion.stopMove()
  
    def Obstacle_L_R_F(self):
        """ obstacle left ,right and front"""
        self.angle = self.angleTurn * almath.TO_RAD
        self.motion.post.moveTo(0, 0, self.angle)

    def turnLeft(self):
        """turn left"""
        self.angle = self.angleTurn * almath.TO_RAD 
        self.motion.post.moveTo(0, 0, 3.14)

    def backTo(self):
        """ back """
        self.motion.moveTo(-1 * self.moveSpeed,0,0)


    def turnRight(self):
        """turn right"""
        self.angle = -1.0 *self.angleTurn * almath.TO_RAD 
        self.motion.post.moveTo(0, 0, -3.14)
""" 
ip = "127.0.0.1"
port = 9559
myBroker = ALBroker("myBroker", #Name broker
   "0.0.0.0",                   #Listen to anyone
    0,                          #Find a free port and use it
    ip,                         #Parent Broker ip
    9559)                       #Parent Broker port

### creat the instance of AvoidanceObstacle
EviteObstacle = AvoidanceObstacle()


try:
    time.sleep(0.7)
    # stop moving with self.runFlag=False ,stop loop while
    #EviteObstacle.setFlag(False) # or EviteObstacle.stop()
    
    EviteObstacle.run()

        
    
except KeyboardInterrupt: #control ^c to stop
    print
    print "Interrupted by user, shutting down"
    EviteObstacle.setFlag(False) # stop the module 
    myBroker.shutdown()
    sys.exit(0)

"""