
import sprotapi as sprotapi
import sprotpkt as sprotpkt
import multiprocessing
import req
import time
from easyNav_pi_dispatcher import DispatcherClient

DATA_SIZE = 16
DEST_PORT_CRUNCHER = 9003
DEST_PORT_ALERT = 9004


def sonar_post_process(ns) :
	httpClient = req.RequestClass(local_mode=1)	

	while(1) :
		time.sleep(1)
		if (ns.data != 0) :
			# Send right sonar HTTP request
			httpClient.post_heartbeat_sonar("right", ns.data['right'])
			# Send left sonar HTTP request
			httpClient.post_heartbeat_sonar("left", ns.data['left'])
			print "Sent sonar to server ", ns.data



def convertPacketToSonarData(strpkt):
    sonarData = { strpkt[0] : strpkt[2:5] }
    return sonarData



sprotapi.SPROTInit("/dev/ttyAMA0", baudrate=115200)
dc = DispatcherClient(port=9005)
dc.start()

sonar1Data = 0
sonar2Data = 0
compassData = 0
footsensData = 0

manager = multiprocessing.Manager()
ns = manager.Namespace()
ns.data = 0

p1 = multiprocessing.Process(target=sonar_post_process, args=(ns,))
p1.start()


while True :

    	# Read a packet
	pkt = sprotapi.SPROTReceive()    

	# Check for error
    	if (not isinstance(pkt, sprotpkt.SPROTPacket)) :
        	print "recv error"
    	else :
		# Check packet type
		strpkt = pkt.data.decode("ascii")

		if (strpkt[0] == b'1') :
			sonar1Data = convertPacketToSonarData(strpkt)
		elif (strpkt[0] == b'2') :
			sonar2Data = convertPacketToSonarData(strpkt)
        	elif (strpkt[0] == b'C') :
			compassData = strpkt[2:5]
		elif (strpkt[0] == b'F') :
			footsensData = strpkt
			
			
		# If both compass and foot sensor data are available, combine them and send to alert
		if (compassData != 0) :
			# Package into cruncher data
			cruncherData = { "angle" : compassData, "distance" : footsensData }
			dc.send(DEST_PORT_CRUNCHER, "angle", cruncherData)
			
			compassData = 0
			if (footsendData != 0) :
				footsensData = 0
				
			print "Foot/angle sensor ==> cruncher ", cruncherData
			
		# If both sonar data are available, combine them and send to alert
		if ((sonar1Data != 0) and (sonar2Data != 0)) :
			sonar1Data.update(sonar2Data)
			combinedSonarData = sonar1Data
			# Send to alert
			dc.send(DEST_PORT_ALERT, 'sonarData', combinedSonarData)
			print "Sonar ==> alert ", combinedSonarData
			# Send to child process for posting to HTTP server
			ns.data = { 'left' : combinedSonarData['1'], 'right' : combinedSonarData['2']  }
			
			sonar1Data = 0
			sonar2Data = 0
			

# End of script
