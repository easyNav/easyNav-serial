
import sprotapi as sprotapi
from easyNav_pi_dispatcher import DispatcherClient

DATA_SIZE = 5
DEST_PORT_CRUNCHER = 9003
DEST_PORT_ALERT = 9004

def convertPacketToSonarData(strpkt):
    sonarData = { strpkt[0] : strpkt[2:5] }
    return sonarData

sprotapi.SPROTInit("/dev/ttyAMA0", baudrate=57600)
#dc = DispatcherClient(port=9005)

sonar1Data = 0
sonar2Data = 0

while True :
    # Read a packet
	pkt = sprotapi.SPROTReceive(DATA_SIZE)
    
	# Check for error
    if (pkt1 == -1) :
        print "recv error"
    else :
		# Check packet type
		strpkt = pkt.data.decode("ascii")
		if (strpkt[0] == b'1') :
			sonar1Data = convertPacketToSonarData(strpkt)
		elif (strpkt[0] == b'2') :
			sonar2Data = convertPacketToSonarData(strpkt)
        elif (strpkt[0] == b'C') :
			compassData = { strpkt[2:5] }
			#dc.send(DEST_PORT_CRUNCHER, 'compassData', compassData)
			print "Compass data to cruncher ", compassData
			
		# If both sonar data are available, combine them and send to alert
		if ((sonar1Data != 0) and (sonar2Data != 0)) :
			sonar1Data.update(sonar2Data)
			combinedSonarData = sonar1Data
			#dc.send(DEST_PORT_ALERT, 'sonarData', combinedSonarData)
			print "Sonar data to alert", combinedSonarData
			sonar1Data = 0
			sonar2Data = 0

# End of script
