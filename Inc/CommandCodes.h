#ifndef __COMMAND_CODES__
#define __COMMAND_CODES__


#define BL_GET_VERSION      0x51
#define BL_GET_HELP         0x52
#define BL_GET_CID          0x53
#define BL_GET_RDP_STATUS   0x54
#define BL_GO_TO_ADDR       0x55
#define BL_FLASH_ERASE      0x56
#define BL_MEM_WRITE        0x57


// Acknowledge codes for informing host
#define BL_ACK              0xA5
#define BL_NACK             0x7F

#define BL_VERSION  1
#endif