import time
import smokesignal
import threading

from easyNav_pi_dispatcher import DispatcherClient

class Alert(object):

    PORT_NAV_MODULE = 9001
    
    # Maximum sonar readings
    SONAR_MAX_DISTANCE = 700
    
    OBSTACLE_RIGHT = 3
    OBSTACLE_LEFT = 2
    OBSTACLE_BOTH = 1
    OBSTACLE_NONE = 0    
    
    # How close an object has to be before it is declared an obstacle (cm)
    OBSTACLE_DIST_THRESHOLD = 50

    def __init__(self):
        
        ## For interprocess comms 
        self.DISPATCHER_PORT = 9004
        self._dispatcherClient = DispatcherClient(port=self.DISPATCHER_PORT)

        ## Attach event listeners upon instantiation (to prevent duplicates)
        self.attachEvents()        

        # Latest sonar readings
        self.sonarLeft = Alert.SONAR_MAX_DISTANCE
        self.sonarRight = Alert.SONAR_MAX_DISTANCE
    
  
    def start(self):
        ## Start inter-process comms
        self._dispatcherClient.start()      
        
    
    def sendAlert(self, alertType):
        print "Alert : ", alertType
        self._dispatcherClient.send(Alert.PORT_NAV_MODULE, 'obstacle', {'status': alertType})
            
        
    # Check for obstacle position and returns OBSTACLE_X, where X is 
    # one of LEFT, RIGHT, BOTH, NONE
    def checkForObstacle(self):
        leftObstacle =  (self.sonarLeft < Alert.OBSTACLE_DIST_THRESHOLD)
        rightObstacle = (self.sonarRight < Alert.OBSTACLE_DIST_THRESHOLD)

        
        if (leftObstacle and rightObstacle):
            return Alert.OBSTACLE_BOTH
        elif (leftObstacle):
            return Alert.OBSTACLE_LEFT
        elif (rightObstacle):
            return Alert.OBSTACLE_RIGHT
        else:
            return Alert.OBSTACLE_NONE


    def convertStr(self,str):
        maxIndex = 3
        for i in range(3):
            if(str[i].isdigit()):
                maxIndex = i

        return str[0:maxIndex+1]


    def attachEvents(self):
        smokesignal.clear()

        @smokesignal.on('sonarData')
        def sonardata(args):
            payload = eval(args.get("payload"))
            
            strSonarLeft = self.convertStr(payload['1'])
            self.sonarLeft = int(strSonarLeft)
            
            strSonarRight = self.convertStr(payload['2'])
            self.sonarRight = int(strSonarRight)

            self.sendAlert(self.checkForObstacle())
                                            
                    
def runMain():
    alert = Alert()
    alert.start()
    
    
if (__name__ == '__main__') :
    runMain()
