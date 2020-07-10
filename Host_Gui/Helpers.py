import struct
import serial
import os

def get_sizeof_file(filename):
    return os.path.getsize(filename)

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



BL_CMD_GET_VERSION    =0x51
BL_CMD_GET_HELP       =0x52
BL_CMD_GET_CID        =0x53
BL_CMD_GET_RDP_STATUS =0x54
BL_CMD_GO_TO_ADDR     =0x55
BL_CMD_FLASH_ERASE    =0x56
BL_CMD_MEM_WRITE      =0x57

cmd_names=["BL_CMD_GET_VERSION","BL_CMD_GET_HELP","BL_CMD_GET_CID","BL_CMD_GET_RDP_STATUS","BL_CMD_GO_TO_ADDR","BL_CMD_FLASH_ERASE","BL_CMD_MEM_WRITE"]

def write2ser(ser,buff):
    if ser.is_open:
        ser.write(struct.pack(">B",buff))

def read_reply(ser):
    if ser.is_open:
        rep_n=str(ser.readline()).split('-')
        if len(rep_n)>1:
            if int(rep_n[1])==127:
                print("Nackowledge is Received")
                return -2
            else:
                print("Ackowledge is Received")
                recvd=ser.readline().decode('utf-8')
                return recvd
        else:
            return -1
    else:
        return -1
def make_buffer_ready_getversion():
    buff=[]
    gv_package_length=6
    for i in range(gv_package_length):
        buff.append(0)
    buff[0]=str(gv_package_length-1)
    buff[1]=str(BL_CMD_GET_VERSION)
    crc32       = get_crc(buff[0:2],2)
    crc32 = crc32 & 0xffffffff
    buff[2] = word_to_byte(crc32,1,1)
    buff[3] = word_to_byte(crc32,2,1)
    buff[4] = word_to_byte(crc32,3,1)
    buff[5] = word_to_byte(crc32,4,1)
    return buff

def make_buffer_ready_getrdp():
    buff=[]
    grdp_package_length=6
    for i in range(grdp_package_length):
        buff.append(0)
    buff[0]=str(grdp_package_length-1)
    buff[1]=str(BL_CMD_GET_RDP_STATUS)
    crc32       = get_crc(buff[0:2],2)
    crc32 = crc32 & 0xffffffff
    buff[2] = word_to_byte(crc32,1,1)
    buff[3] = word_to_byte(crc32,2,1)
    buff[4] = word_to_byte(crc32,3,1)
    buff[5] = word_to_byte(crc32,4,1)
    return buff

def make_buffer_ready_getCid():
    buff=[]
    gcid_package_length=6
    for i in range(gcid_package_length):
        buff.append(0)
    buff[0]=str(gcid_package_length-1)
    buff[1]=str(BL_CMD_GET_CID)
    crc32       = get_crc(buff[0:2],2)
    crc32 = crc32 & 0xffffffff
    buff[2] = word_to_byte(crc32,1,1)
    buff[3] = word_to_byte(crc32,2,1)
    buff[4] = word_to_byte(crc32,3,1)
    buff[5] = word_to_byte(crc32,4,1)
    return buff

def make_buffer_ready_getscmds():
    buff=[]
    gh_package_length=6
    for i in range(gh_package_length):
        buff.append(0)
    buff[0]=str(gh_package_length-1)
    buff[1]=str(BL_CMD_GET_HELP)
    crc32       = get_crc(buff[0:2],2)
    crc32 = crc32 & 0xffffffff
    buff[2] = word_to_byte(crc32,1,1)
    buff[3] = word_to_byte(crc32,2,1)
    buff[4] = word_to_byte(crc32,3,1)
    buff[5] = word_to_byte(crc32,4,1)
    return buff

def make_buffer_ready_jumpaddr(adress):
    gaddress_package_length=10
    buff=[]
    for i in range(gaddress_package_length):
        buff.append(0)
    buff[0]=str(gaddress_package_length-1)
    buff[1]=str(BL_CMD_GO_TO_ADDR)
    buff[2]=word_to_byte(adress,1,1)
    buff[3]=word_to_byte(adress,2,1)
    buff[4]=word_to_byte(adress,3,1)
    buff[5]=word_to_byte(adress,4,1)
    crc32 = get_crc(buff[0:6],6)
    crc32 = crc32 & 0xffffffff
    buff[6] = word_to_byte(crc32,1,1)
    buff[7] = word_to_byte(crc32,2,1)
    buff[8] = word_to_byte(crc32,3,1)
    buff[9] = word_to_byte(crc32,4,1)
    return buff

def make_buffer_ready_eraseflash(SectorNo,nofsector):
        rflash_package_length=8
        buff=[]
        for i in range(rflash_package_length):
            buff.append(0)
        buff[0]=str(rflash_package_length-1)
        buff[1]=str(BL_CMD_FLASH_ERASE)
        buff[2]=SectorNo
        buff[3]=nofsector
        crc32 = get_crc(buff[0:4],4)
        crc32 = crc32 & 0xffffffff
        buff[4] = word_to_byte(crc32,1,1)
        buff[5] = word_to_byte(crc32,2,1)
        buff[6] = word_to_byte(crc32,3,1)
        buff[7] = word_to_byte(crc32,4,1)
        return buff


def getReply(ser,cmd):
    if ser.is_open:
        ackrep=ser.readline().decode("utf-8")
        # İf ack is received
        if "165" in ackrep:
            replylen=int(ackrep.split("-")[2])
            reply=ser.read(replylen).decode("utf-8")
            if str(cmd) in reply:
                textreaded=reply.split("-")[1]
                return textreaded


def getRDP(ser):
    databuff=make_buffer_ready_getrdp()
    if ser.is_open:
        write2ser(ser,int(databuff[0]))
        for i_byte in databuff[1:6]:
            write2ser(ser,int(i_byte))

def getVersion(ser):
    databuff=make_buffer_ready_getversion()
    if ser.is_open:
        write2ser(ser,int(databuff[0]))
        for i_byte in databuff[1:6]:
            write2ser(ser,int(i_byte))

def getCID(ser):
    databuff=make_buffer_ready_getCid()
    if ser.is_open:
        write2ser(ser,int(databuff[0]))
        for i_byte in databuff[1:6]:
            write2ser(ser,int(i_byte))

def getSCMDS(ser):
    databuff=make_buffer_ready_getscmds()
    if ser.is_open:
        write2ser(ser,int(databuff[0]))
        for i_byte in databuff[1:6]:
            write2ser(ser,int(i_byte))


def JUMPaddrr(ser,addr):
    databuff=make_buffer_ready_jumpaddr(addr)
    if ser.is_open:
        write2ser(ser,int(databuff[0]))
        for i_byte in databuff[1:10]:
            write2ser(ser,int(i_byte))

def eraseSector(ser,SectorNo,NofSector):
    databuff=make_buffer_ready_eraseflash(SectorNo,NofSector)
    if ser.is_open:
        write2ser(ser,int(databuff[0]))
        for i_byte in databuff[1:8]:
            write2ser(ser,int(i_byte))