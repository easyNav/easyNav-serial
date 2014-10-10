###### Protocol constants #######

PACKET_SIZE =                        32                           # 50-bytes fixed packet size
HEADER_LENGTH =                      3                            # Header size in bytes
FIELD_DT_LENGTH =                    1                            # DT field size in bytes
FIELD_TYPE_LENGTH =                  1                            # TYPE field size in bytes
FIELD_DLEN_LENGTH =                  1                            # DATA_LENGTH field size in bytes
FIELD_CHECKSUM_LENGTH =              1                            # CHECKSUM field size in bytes

# The length of the DATA field in bytes
FIELD_DATA_LENGTH =                  (PACKET_SIZE - HEADER_LENGTH - FIELD_CHECKSUM_LENGTH)

FIELD_TYPE_OFFSET =                  0                            # TYPE field offset in bytes
FIELD_DT_OFFSET =                    1                            # DT/TYPE field offset in bytes
FIELD_DLEN_OFFSET =                  2                            # DATA_LENGTH field offset in bytes
FIELD_CHECKSUM_OFFSET =              PACKET_SIZE - 1              # CHECKSUM field offset in bytes
FIELD_DATA_OFFSET =                  HEADER_LENGTH                # DATA field offset in bytes

# ARQ Parameters
SPROT_SEND_TIMEOUT =                 5                            # Default send timeout in ms
SPROT_RECV_TIMEOUT =                 5                            # Default receive timeout ms
MAX_RETRIES_SESSION_INIT =           3                            # Maximum retries for session initialization
MAX_RETRIES_SESSION_END =            3                            # Maximum retries for session end
MAX_RETRIES_DATA_TRANSFER =          3                            # Maximum retries for data transfer
AUTORESET_THRESHOLD =                3                            # No. of successive timeouts in a row required to trigger auto-reset

# Protocol-Field constants
PACKET_TYPE_ACK =                    0x01
PACKET_TYPE_NAK =                    0x02
PACKET_TYPE_HELLO =                  0x03
PACKET_TYPE_END =                    0x04
PACKET_TYPE_DATA =                   0x05

# Bitwise-OR with PACKET_TYPE field to embed DATA_TOGGLE value (0 or 1 bit)
DATA_TOGGLE_0 =                      0x00
DATA_TOGGLE_1 =                      0x01

# Error constants
SPROT_ERROR_NONE =                    0x00
SPROT_ERROR_TIMEOUT =                 0xF0
SPROT_ERROR_CHECKSUM =                0xF1
SPROT_ERROR_SESSION_INIT_FAILURE =    0xF2
SPROT_ERROR_SESSION_ENDED =           0xF3

#Default baudrate to be used
DEFAULT_BAUDRATE =                    9600

