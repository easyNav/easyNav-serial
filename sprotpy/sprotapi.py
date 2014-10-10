# python module containing serial port functions utilizing Serial Protocol (sprot)

import serial as serial
import sprotcfg as sprotcfg
import sprotint as sprotint
import sprotapi as sprotapi
import sprotpkt as sprotpkt


protocolInitiazed = False
sessionStarted = False
sendDTBit = 0
recvDTBit = 0 
sendTimeouts = 0
recvTimeouts = 0
serialPort = None


def SPROTInit(portName, baudrate=9600):
	if sprotapi.protocolInitiazed :
		return
	else :
		sprotapi.serialPort = serial.Serial(portName, baudrate=baudrate, timeout=sprotcfg.SPROT_RECV_TIMEOUT)
		sprotapi.protocolInitiazed = True
		
		
def SPROTReset():
	sprotapi.sessionStarted = False
	sprotapi.sendDTBit = 0
	sprotapi.recvDTBit = 0


def SPROTClose():
	retries = 0
	doRetry = True
	
	while doRetry :
		if (not sprotapi.protocolInitiazed) or (not sprotapi.sessionStarted) :
			return
		else :
			sprotint.sendControlPacket(sprotcfg.PACKET_TYPE_END)
			controlPacket = sprotint.receivePacket(sprotcfg.SPROT_RECV_TIMEOUT)
			retries += 1
			doRetry = ((controlPacket != sprotcfg.PACKET_TYPE_ACK) and (retries < sprotcfg.MAX_RETRIES_SESSION_END))

	sprotapi.protocolInitiazed = False
	serialPort.close()
	SPROTReset()
	
	
def SPROTReceive(timeout=sprotcfg.SPROT_RECV_TIMEOUT):
	
	doRetry = True
	checksumError = False
	invalidDTBit = False 
	invalidPacketType = False
	ignoreHellos = False
	retries = 0
	timeoutOccured = False
	
	if not sprotapi.protocolInitiazed:
		return -1

	# If a communications session has not yet started, start it
	if not sprotapi.sessionStarted:
		sessionStartOK = (sprotint.waitForSessionStart(timeout) != -1)
		
		if not sessionStartOK:
			return -1		
		else :
			sprotapi.sessionStarted = True
			ignoreHellos = True
	else :
		ignoreHellos = False
	
	while doRetry :
		received = sprotint.receivePacket(timeout)
		
		if isinstance(received, sprotpkt.SPROTPacket) :
			invalidDTBit = (received.dtBit != sprotapi.recvDTBit)
			invalidPacketType = (received.type != sprotcfg.PACKET_TYPE_DATA)
		else :
			# Determine when to reset current session
			if (received == sprotcfg.SPROT_ERROR_TIMEOUT) :	
				timeoutOccured = True		
				sprotapi.recvTimeouts += 1
				if (sprotapi.recvTimeouts == sprotcfg.AUTORESET_THRESHOLD) :				
					sprotapi.recvTimeouts = 0
					sessionStarted = False				
				break			
			else :			
				recvTimeouts = 0
			
			checksumError = (received == sprotcfg.SPROT_ERROR_CHECKSUM)
		
		doRetry = (checksumError or invalidDTBit or invalidPacketType) and (retries < sprotcfg.MAX_RETRIES_DATA_TRANSFER)

		if (received == sprotcfg.SPROT_ERROR_CHECKSUM):
			# Send NAK for checksum error
			sprotint.sendControlPacket(sprotcfg.PACKET_TYPE_NAK)		
		elif (invalidDTBit):		
			# Re-send ACK for repeated transmission
			sprotint.sendControlPacket(sprotcfg.PACKET_TYPE_ACK)		
		elif(invalidPacketType):		
			if(received.type == sprotcfg.PACKET_TYPE_HELLO):			
				# Ignore repeated HELLO packets if required
				if not ignoreHellos :
					sprotint.sendControlPacket(sprotcfg.PACKET_TYPE_ACK);
					sprotapi.recvDTBit = 0;
					ignoreHellos = True;
				continue;
		else :
			ignoreHellos = False
			
		if doRetry : 
			retries += 1
							
	if (timeoutOccured or invalidDTBit or invalidPacketType) :
		sprotapi.recvDTBit = 0	
		return -1
	else :
		# Send ACK for successful data transfer
		sprotint.sendControlPacket(sprotcfg.PACKET_TYPE_ACK)

		# Toggle alternate bit sequence value
		sprotapi.recvDTBit = 1 if (sprotapi.recvDTBit == 0) else 0		
		return received
		

def SPROTSend(data, timeout=sprotcfg.SPROT_SEND_TIMEOUT):

	doRetry = True
	invalidPacketType = False
	timeoutOccured = False
	checksumError = False
	retries = 0

	# If a communications session has not yet started, start it
	if (not sprotapi.sessionStarted and (sprotint.startSession(timeout) == -1)) :
		return -1
	else :
		sprotapi.sessionStarted = True
	
	packet = sprotint.createPacket(sprotapi.sendDTBit, sprotcfg.PACKET_TYPE_DATA, data)
	
	while (doRetry):
		sprotint.sendPacket(packet)

		# Wait for reply
		reply = sprotint.receivePacket(timeout)
		
		# Determine when to reset current session
		if (not isinstance(reply, sprotpkt.SPROTPacket)) :
			if (reply == sprotcfg.SPROT_ERROR_TIMEOUT) :	
				timeoutOccured = True		
				sprotapi.sendTimeouts += 1
				if (sprotapi.sendTimeouts == sprotcfg.AUTORESET_THRESHOLD) :				
					sprotapi.sendTimeouts = 0
					sprotapi.sessionStarted = False				
				break
			elif (reply == sprotcfg.SPROT_ERROR_CHECKSUM) :
				checksumError = True;			
		else :			
			sendTimeouts = 0

		invalidPacketType = isinstance(reply, sprotpkt.SPROTPacket) and (reply.type != sprotcfg.PACKET_TYPE_ACK)
		doRetry =  invalidPacketType and (retries < sprotcfg.MAX_RETRIES_DATA_TRANSFER)

		if (doRetry):
			retries += 1	

	if (timeoutOccured or checksumError or invalidPacketType) :
		sprotapi.sendDTBit = 0
		return -1
	else :
		sprotapi.sendDTBit = 1 if (sprotapi.sendDTBit == 0) else 0
		return 0
	
