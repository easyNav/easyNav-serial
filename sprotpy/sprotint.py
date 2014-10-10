# Serial Protocol internal function definitions

import sprotcfg as sprotcfg
import sprotapi as sprotapi
import sprotpkt as sprotpkt


def createPacket(dtBit, packetType, data):
    
    rawPacket = bytearray(sprotcfg.PACKET_SIZE)
    rawPacket[sprotcfg.FIELD_TYPE_OFFSET] = packetType
    rawPacket[sprotcfg.FIELD_DT_OFFSET] = dtBit
    rawPacket[sprotcfg.FIELD_DLEN_OFFSET] = len(data);
    rawPacket[sprotcfg.FIELD_DATA_OFFSET:sprotcfg.FIELD_DATA_OFFSET+len(data)] = data
    packet = sprotpkt.SPROTPacket(rawPacket)

    # Generate checksum for this packet
    packet.checksum = generateChecksum(packet)

    return packet


def generateChecksum(packet):
    
    computeLength = sprotcfg.HEADER_LENGTH + packet.dataLength
    checksum = 0
    
    for i in range(computeLength) :
        checksum = checksum ^ packet.raw[i]
    
    return checksum


def receivePacket(timeout=sprotcfg.SPROT_RECV_TIMEOUT):
        
    sprotapi.serialPort.timeout = timeout
    recvBytes = bytearray(sprotapi.serialPort.read(sprotcfg.PACKET_SIZE))
        
    if (len(recvBytes) < sprotcfg.PACKET_SIZE) :
        return sprotcfg.SPROT_ERROR_TIMEOUT
    
    packet = sprotpkt.SPROTPacket(recvBytes)
            
    # Check for errors
    checksum = generateChecksum(packet)

    if (checksum != packet.checksum):    
        return sprotcfg.SPROT_ERROR_CHECKSUM
    else :
        return packet
    

def sendPacket(packet):
    sprotapi.serialPort.write(packet.toByteArray())


def sendControlPacket(packetType):
    controlPacket = bytearray(sprotcfg.PACKET_SIZE)
    controlPacket[sprotcfg.FIELD_TYPE_OFFSET] = packetType
    controlPacket[sprotcfg.FIELD_DLEN_OFFSET] = 0
    controlPacket[sprotcfg.FIELD_CHECKSUM_OFFSET] = packetType
    sprotapi.serialPort.write(controlPacket)


def startSession(timeout):
    doRetry = True
    retries = 0

    while(doRetry):
        sendControlPacket(sprotcfg.PACKET_TYPE_HELLO)
        recv = receivePacket(timeout)

        if (isinstance(recv, sprotpkt.SPROTPacket) and (recv.type == sprotcfg.PACKET_TYPE_ACK)):
            return sprotcfg.SPROT_ERROR_NONE
        elif (recv == -1):
            return -1
        else :
            retries += 1
            doRetry = False if (retries > sprotcfg.MAX_RETRIES_SESSION_INIT) else 1
 
    return -1


def waitForSessionStart(timeout):
    doRetry = True
    retries = 0

    while (doRetry):  
        recv = receivePacket(timeout)

        if (isinstance(recv, sprotpkt.SPROTPacket) and (recv.type == sprotcfg.PACKET_TYPE_HELLO)):     
            sendControlPacket(sprotcfg.PACKET_TYPE_ACK)
            return sprotcfg.SPROT_ERROR_NONE        
        elif (recv == -1):       
            return -1       
        else :      
            retries += 1
            doRetry = False if (retries > sprotcfg.MAX_RETRIES_SESSION_INIT) else 1
   
    return -1

