import serial
import struct

ser = serial.Serial('COM5', 115200, timeout=0,parity=serial.PARITY_NONE, rtscts=1)

BL_CMD_GET_VERSION                              =0x51
BL_CMD_GET_HELP                                 =0x52
BL_CMD_GET_CID                                  =0x53
BL_CMD_GET_RDP_STATUS                           =0x54
BL_CMD_GO_TO_ADDR                               =0x55
BL_CMD_FLASH_ERASE                              =0x56
BL_CMD_MEM_WRITE                                =0x57



def word_to_byte(addr, index , lowerfirst):
    value = (addr >> ( 8 * ( index -1)) & 0x000000FF )
    return value

def get_crc(buff, length):
    Crc = 0xFFFFFFFF
    for i in range(length):
        buff[i]=int(buff[i])
    for data in buff[0:length]:
        Crc = Crc ^ data
        for i in range(32):
            if(Crc & 0x80000000):
                Crc = (Crc << 1) ^ 0x04C11DB7
            else:
                Crc = (Crc << 1)
    return Crc

def write_to_ser(data):
    ser.write(struct.pack(">B",data))

def read_knowledge():
    rep_n=str(ser.readline()).split('-')
    if len(rep_n)>1:
        if int(rep_n[1])==127:
            print("Nacknowledge is received")
        else:
            print("Ackowledge is Received")
            recvd=ser.readline().decode('utf-8')
            return recvd
    else:
        return "Unsuccesfull reading"


databuff=[]
while True:
    
    for i in range(255):
        databuff.append(0)
    print("----------------------------\n")
    print("- For getting version : 1  -\n")
    print("- For getting Help    : 2  -\n")
    print("- For getting CID     : 3  -\n")
    print("----------------------------\n")
    opt=int(input('Enter option : '))
    if opt == 0:
        break
    elif opt==1:
        gv_package_length=6
        databuff[0]=str(gv_package_length-1)
        databuff[1]=str(BL_CMD_GET_VERSION)
        crc32       = get_crc(databuff[0:2],2)
        crc32 = crc32 & 0xffffffff
        databuff[2] = word_to_byte(crc32,1,1)
        databuff[3] = word_to_byte(crc32,2,1)
        databuff[4] = word_to_byte(crc32,3,1)
        databuff[5] = word_to_byte(crc32,4,1)
        write_to_ser(int(databuff[0]))
        for i_byte in databuff[1:6]:
            write_to_ser(int(i_byte))
        bl_rep=read_knowledge()
        print(bl_rep)

    elif opt==2:
        gh_package_length=6
        databuff[0]=str(gh_package_length-1)
        databuff[1]=str(BL_CMD_GET_HELP)
        crc32       = get_crc(databuff[0:2],2)
        crc32 = crc32 & 0xffffffff
        databuff[2] = word_to_byte(crc32,1,1)
        databuff[3] = word_to_byte(crc32,2,1)
        databuff[4] = word_to_byte(crc32,3,1)
        databuff[5] = word_to_byte(crc32,4,1)
        write_to_ser(int(databuff[0]))
        for i_byte in databuff[1:6]:
            write_to_ser(int(i_byte))
        bl_rep=read_knowledge().split('-')
        for i in range(1,len(bl_rep)-1):
            print(f"Supported command code {hex(int(bl_rep[i]))}")
    elif opt==3:
        gcid_package_length=6
        databuff[0]=str(gcid_package_length-1)
        databuff[1]=str(BL_CMD_GET_CID)
        crc32       = get_crc(databuff[0:2],2)
        crc32 = crc32 & 0xffffffff
        databuff[2] = word_to_byte(crc32,1,1)
        databuff[3] = word_to_byte(crc32,2,1)
        databuff[4] = word_to_byte(crc32,3,1)
        databuff[5] = word_to_byte(crc32,4,1)
        write_to_ser(int(databuff[0]))
        for i_byte in databuff[1:6]:
            write_to_ser(int(i_byte))
        bl_rep=read_knowledge().split('-')
        if len(bl_rep)==3:
            print(f"The Chip İd {hex(int(bl_rep[1]))}")
        else:
            pass
    else:
        print("Unrecognized command")
ser.close()



