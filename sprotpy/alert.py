import time
import smokesignal
import threading

from easyNav_pi_dispatcher import DispatcherClient

class Alert(object):

    # Port for voice module
    PORT_VOICE_MODULE = 9002
    PORT_NAV_MODULE = 9001
    
    ## Run Levels here
    RUNLVL_NORMAL = 0
    RUNLVL_WARNING_OBSTACLE = 1
    
    # Maximum sonar readings
    SONAR_MAX_DISTANCE = 700
    
    # Voice alerts
    VOICE_ALERT_OBSTACLE_LEFT = "keep right"
    VOICE_ALERT_OBSTACLE_RIGHT = "keep left"
    VOICE_ALERT_STOP= "stop"
    VOICE_ALERT_PROCEED = "proceed"
    
    OBSTACLE_RIGHT = 3
    OBSTACLE_LEFT = 2
    OBSTACLE_BOTH = 1
    OBSTACLE_NONE = 0    


    # How much time to wait in secs before re-accessing situation and determining next movement
    # (applicable in obstacle avoidance mode)
    OBSTACLE_AVOIDANCE_WAIT_INTERVAL = 3
    
    # How close an object has to be before it is declared an obstacle (cm)
    OBSTACLE_DIST_THRESHOLD = 100
	
    # How many times must obstacle be detected before it is confirmed
    OBSTACLE_CONFIRMATION_COUNT = 3


    def __init__(self):
        
        ## For interprocess comms 
        self.DISPATCHER_PORT = 9004
        self._dispatcherClient = DispatcherClient(port=self.DISPATCHER_PORT)

        ## Attach event listeners upon instantiation (to prevent duplicates)
        self.attachEvents()        
        
        # Whether obstacle avoidance is in progress
        self.obstacleAvoidanceInProgress = False
                
        # Keep track of what the last voice alert was so we don't irritate user unnecessarily!
        self.lastVoiceAlert = None

        # Latest sonar readings
	self.sonarLeft = Alert.SONAR_MAX_DISTANCE
        self.sonarRight = Alert.SONAR_MAX_DISTANCE
	
  
    def start(self):
        ## Start inter-process comms
        self._dispatcherClient.start()      
  	  
    
    def sendAlert(self, alertType):
        # Don't send successive stop commands - user may get angry!
        ignoreAlert = (self.lastVoiceAlert == Alert.VOICE_ALERT_STOP) and (alertType == Alert.VOICE_ALERT_STOP)
        
        if (not ignoreAlert):
            #self.lastVoiceAlert = alertType
            print "Alert sent : ", alertType, "\n"
            #self._dispatcherClient.send(Alert.PORT_VOICE_MODULE, 'say', {'text': alertType})
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
        
        
    def performObstacleAvoidance(self):
        hasObstacle = True
	firstLoopRun = True

        while (hasObstacle) :
            # Wait for user to react - he's not "The Flash" you know!
            time.sleep(Alert.OBSTACLE_AVOIDANCE_WAIT_INTERVAL)
            currentObstacle = self.checkForObstacle()
	
	   
            #if (currentObstacle == Alert.OBSTACLE_LEFT):
                #voiceAlert = Alert.VOICE_ALERT_OBSTACLE_LEFT 
            #    navAlert = Alert.VOICE_ALERT_OBSTACLE_LEFT             	
	    #elif (currentObstacle == Alert.OBSTACLE_RIGHT):
                #voiceAlert = Alert.VOICE_ALERT_OBSTACLE_LEFT 
            #    navAlert = Alert.VOICE_ALERT_OBSTACLE_RIGHT 
            #elif (currentObstacle == Alert.OBSTACLE_BOTH):
                #voiceAlert = Alert.VOICE_ALERT_OBSTACLE_LEFT 
            #    navAlert = Alert.VOICE_ALERT_STOP 
            #else :
            #    hasObstacle = False
            #    voiceAlert = Alert.VOICE_ALERT_PROCEED

            #self.sendAlert(voiceAlert)
	    self.sendAlert(currentObstacle)

	# We have finished the obstacle avoidance loop here
        self.obstacleAvoidanceInProgress = False


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
	        
        	if( not self.obstacleAvoidanceInProgress ):
        		if ( self.checkForObstacle() != Alert.OBSTACLE_NONE ):
                		self.obstacleAvoidanceInProgress = True
                		self.sendAlert(Alert.VOICE_ALERT_STOP)
				sonarDataThread = threading.Thread(target=self.performObstacleAvoidance)
	 			sonarDataThread.start()
 		               	                
                    
def runMain():
	alert = Alert()
	alert.start()
    
    
if (__name__ == '__main__') :
	runMain()
