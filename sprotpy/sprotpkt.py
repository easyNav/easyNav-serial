# SPROTPacket class represents a Serial Protocol Packet

# Constructor :
# SPROTPacket(rawPacket=none)
#    rawPacket - A bytearray or bytes that contains the raw packet data

import sprotcfg as sprotcfg


class SPROTPacket:
    def __init__(self, rawPacket=None):
        self.dtBit = 0;
        self.type = 0
        self.dataLength = 0;
        self.data = None
        self.checksum = 0
        
        if(rawPacket == None):
            return
        
        # Construct packet from given array of bytes
        self.type = rawPacket[sprotcfg.FIELD_TYPE_OFFSET]
        self.dtBit = rawPacket[sprotcfg.FIELD_DT_OFFSET]
        self.dataLength = rawPacket[sprotcfg.FIELD_DLEN_OFFSET]
        self.data = bytearray(rawPacket[sprotcfg.FIELD_DATA_OFFSET:sprotcfg.FIELD_DATA_OFFSET + self.dataLength])
        self.checksum = rawPacket[sprotcfg.FIELD_CHECKSUM_OFFSET]
        self.raw = rawPacket
        
    
    def toByteArray(self):
        self.raw = bytearray(sprotcfg.PACKET_SIZE)
        self.raw[sprotcfg.FIELD_TYPE_OFFSET] = self.type
        self.raw[sprotcfg.FIELD_DT_OFFSET] = self.dtBit       
        self.raw[sprotcfg.FIELD_DLEN_OFFSET] = len(self.data);
        self.raw[sprotcfg.FIELD_DATA_OFFSET:sprotcfg.FIELD_DATA_OFFSET+len(self.data)] = self.data
        self.raw[sprotcfg.FIELD_CHECKSUM_OFFSET] = self.checksum
        return self.raw


    def printPacket(self):
        print "pktinfo :  toggle=", self.dtBit, "  dlen=", self.dataLength, "  data=", self.data, "  checksum=", format(self.checksum, "02x")


