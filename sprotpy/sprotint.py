# Serial Protocol internal function definitions

import sprotcfg as sprotcfg
import sprotapi as sprotapi
import sprotpkt as sprotpkt


def createPacket(data):
    
    rawPacket = bytearray(sprotcfg.PACKET_SIZE)
    rawPacket[sprotcfg.FIELD_PM_OFFSET] = sprotcfg.SPROT_PROTOCOL_MARKER
    rawPacket[sprotcfg.FIELD_DLEN_OFFSET] = len(data);
    rawPacket[sprotcfg.FIELD_DATA_OFFSET:sprotcfg.FIELD_DATA_OFFSET+len(data)] = data
	rawPacket[sprotcfg.FIELD_CHECKSUM_OFFSET] = generateChecksum(packet)
    packet = sprotpkt.SPROTPacket(rawPacket)

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
        return sprotcfg.SPROT_ERROR
    
    packet = sprotpkt.SPROTPacket(recvBytes)
            
    # Check for errors
    checksum = generateChecksum(packet)

    if (checksum != packet.checksum):    
        return sprotcfg.SPROT_ERROR
    else :
        return packet
    

def sendPacket(packet):
    sprotapi.serialPort.write(packet.toByteArray())
