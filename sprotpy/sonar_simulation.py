# Performs sonar simulation
import threading
import time
import sonar_simulation
from easyNav_pi_dispatcher import DispatcherClient

OWN_PORT = 9005
DEST_PORT = 9004
INTERVAL_SECS = 0.5

SONAR_MAX = 600
OBSTACLE_THRESHOLD = 70
NONE = "none"
LEFT = "left"
RIGHT = "right"
BOTH = "both"

obstacle_location = NONE
sonar1 = SONAR_MAX
sonar2 = SONAR_MAX

despClient = DispatcherClient(port=OWN_PORT)


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


def sendSonarReading():
    while (True):
        sonarData = {'1':sonar_simulation.sonar1, '2':sonar_simulation.sonar2}
        despClient.send(DEST_PORT, 'sonarData', sonarData)
        print "Sent sonarData=", sonarData
        time.sleep(INTERVAL_SECS)
    
sonarThread = threading.Thread(target=sendSonarReading)
sonarThread.start()
quit = False

while (not quit):
    sonar_simulation.obstacle_location = input("Obstacle (right, left, none, both): ")
    createObstacle();

# End of program
    
    
    