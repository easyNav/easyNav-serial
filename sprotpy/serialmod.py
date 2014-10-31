
import sprotapi as sprotapi
import sprotpkt as sprotpkt
import multiprocessing
import req
import time
import threading
import serialmod as serialmod
from easyNav_pi_dispatcher import DispatcherClient

DATA_SIZE = 16
DEST_PORT_CRUNCHER = 9003
DEST_PORT_ALERT = 9004


# Posts sonar data to server
def sonar_post_process(ns) :
	httpClient = req.RequestClass(local_mode=1)	

	while (True) :
		time.sleep(1)
		if (ns.data != 0) :
			try :
				# Send right sonar HTTP request
				httpClient.post_heartbeat_sonar("right", ns.data['right'])
				# Send left sonar HTTP request
				httpClient.post_heartbeat_sonar("left", ns.data['left'])
				print "Sent sonar to server ", ns.data
			except :
				print "Server communications failed."
				pass


# Extract sonar data from generic packet
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
footsensMutex = threading.Lock()

manager = multiprocessing.Manager()
ns = manager.Namespace()
ns.data = 0

p1 = multiprocessing.Process(target=sonar_post_process, args=(ns,))
#p1.start()


# easyNav-dispatcher communications
def dispatchData() :			
			
	while True :
		time.sleep(0.001)
		
		# Send compass data, set distance to zero if not available
		if (serialmod.compassData != 0) :
			# Acquire mutex lock on foot sensor data so that we don't miss any updates to it
			serialmod.footsensMutex.acquire(blocking=True)
			
			# Package into cruncher data
			cruncherData = { "angle" : serialmod.compassData, "distance" : serialmod.footsensData }			
			serialmod.dc.send(DEST_PORT_CRUNCHER, 'angle', cruncherData)			
			serialmod.compassData = 0
			
			# Clear footsens data if we have consumed it
			if (serialmod.footsensData != 0) :
				serialmod.footsensData = 0
				
			# Release the mutex lock after consuming footsend data
			serialmod.footsensMutex.release()
	
			print "Foot/angle sensor ==> cruncher ", cruncherData
			
		# If both sonar data are available, combine them and send to alert
		if ((serialmod.sonar1Data != 0) and (serialmod.sonar2Data != 0)) :
			serialmod.sonar1Data.update(serialmod.sonar2Data)
			combinedSonarData = serialmod.sonar1Data
			
			# Send to alert
			serialmod.dc.send(DEST_PORT_ALERT, 'sonarData', combinedSonarData)
			print "Sonar ==> alert ", combinedSonarData
			# Send to child process for posting to HTTP server
			#serialmod.ns.data = { 'left' : combinedSonarData['1'], 'right' : combinedSonarData['2']  }
		
			# Clear sonar data after we have consumed them
			serialmod.sonar1Data = 0
			serialmod.sonar2Data = 0


# Run the easyNav dispatcher in a separate thread so it does not hog our serial read
dispatcherThread = threading.Thread(target=serialmod.dispatchData)
dispatcherThread.start()		


# Strips trailing zeroes if required
# def removeNullChars(self,str):
	# maxIndex = 3
	# for i in range(3):
		# if(str[i].isdigit() or str[i] == '.'):
			# maxIndex = i

	# return str[0:maxIndex+1]
	
		
while True :

    	# Read a packet
	pkt = sprotapi.SPROTReceive()    

	# Check for error
    	if (not isinstance(pkt, sprotpkt.SPROTPacket)) :
        	print "recv error"
    	else :
		# Check packet type
		#pkt.printPacket()
		strpkt = pkt.data.decode("ascii")

		if (strpkt[0] == b'1') :
			sonar1Data = convertPacketToSonarData(strpkt)
		elif (strpkt[0] == b'2') :
			sonar2Data = convertPacketToSonarData(strpkt)
        	elif (strpkt[0] == b'C') :
			compassData = strpkt[2:5]
		elif (strpkt[0] == b'F') :
			footsensMutex.acquire(blocking=True)
			footsensData = strpkt[2:10]
			footsensMutex.release()



# End of serialmod
