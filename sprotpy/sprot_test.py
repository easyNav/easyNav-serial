
import sprotapi as sprotapi
import time as time
#from easyNav_pi_dispatcher import DispatcherClient

DATA_SIZE = 5
DEST_PORT = 9004

def convertSPROTPacketToJson(packet):
    strpkt = packet.data.decode("ascii")
    jsonpkt = '"' + strpkt[0] + '"' + ':"' + strpkt[2:5] + '"'
    return jsonpkt

sprotapi.SPROTInit("COM1", baudrate=9600)

while True :
    pkt1 = sprotapi.SPROTReceive(DATA_SIZE)
    pkt2 = sprotapi.SPROTReceive(DATA_SIZE)
    
    if ((pkt1 == -1) or (pkt2 == -1)) :
        print "recv error"
    else :
        jsonSonar1 = convertSPROTPacketToJson(pkt1)
        jsonSonar2 = convertSPROTPacketToJson(pkt2)
        sonarData = "{" + jsonSonar1 + "," + jsonSonar1 +"}"
        
        #dc = DispatcherClient(port=9005)
        #dc.send(DEST_PORT, 'sonarData', sonarData)
        print "Sent sonar data to alert (", sonarData, ")"
        
    time.sleep(0.05)
        

    
    

