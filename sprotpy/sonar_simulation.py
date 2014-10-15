# Performs sonar simulation
import threading
import time
import sonar_simulation
import alert
#from easyNav_pi_dispatcher import DispatcherClient

OWN_PORT = 9005
DEST_PORT = 9004
INTERVAL_SECS = 2

SONAR_MAX = 600
OBSTACLE_THRESHOLD = 70
NONE = "none"
LEFT = "left"
RIGHT = "right"
BOTH = "both"

obstacle_location = NONE
sonar1 = SONAR_MAX
sonar2 = SONAR_MAX
sonarData = None

#despClient = DispatcherClient(port=OWN_PORT)
alertMod = alert.Alert()

def createObstacle():
    if (sonar_simulation.obstacle_location == NONE):
        sonar_simulation.sonar1 = SONAR_MAX
        sonar_simulation.sonar2 = SONAR_MAX
    elif (sonar_simulation.obstacle_location == RIGHT):
        sonar_simulation.sonar1 = SONAR_MAX
        sonar_simulation.sonar2 = OBSTACLE_THRESHOLD - 10
    elif (sonar_simulation.obstacle_location == LEFT):
        sonar_simulation.sonar1 = OBSTACLE_THRESHOLD - 10
        sonar_simulation.sonar2 = SONAR_MAX
    elif (sonar_simulation.obstacle_location == BOTH):
        sonar_simulation.sonar1 = OBSTACLE_THRESHOLD - 10
        sonar_simulation.sonar2 = OBSTACLE_THRESHOLD - 10

def runAlertModule():
        sonar_simulation.alertMod.sonardata(sonar_simulation.sonarData)

def sendSonarReading():
    while (True):
        sonar_simulation.sonarData = {'1':sonar_simulation.sonar1, '2':sonar_simulation.sonar2}
        alertThread = threading.Thread(target=runAlertModule)
        alertThread.start()
        #despClient.send(DEST_PORT, 'sonarData', sonarData)
        #print "Sent sonarData=", sonar_simulation.sonarData, "\n"
        time.sleep(INTERVAL_SECS)
        

sonarThread = threading.Thread(target=sendSonarReading)
sonarThread.start()


while (True):
    sonar_simulation.obstacle_location = input()
    createObstacle();

# End of program
    
    
    