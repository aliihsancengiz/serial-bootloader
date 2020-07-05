import serial
import struct
import time

ser = serial.Serial('COM13', 115200, timeout=0,parity=serial.PARITY_NONE, rtscts=1)

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
    
    for i in range(100):
        databuff.append(0)
    print("---------------------------------\n")
    print("- For getting version      : 1  -\n")
    print("- For getting Help         : 2  -\n")
    print("- For getting CID          : 3  -\n")
    print("- For getting RDP Status   : 4  -\n")
    print("- For jumping Adress       : 5  -\n")
    print("- For Flash Erase          : 6  -\n")
    print("- For Memory Write         : 7  -\n")
    print("---------------------------------\n")
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
            print(bl_rep)
    elif opt==4:
        grdp_package_length=6
        databuff[0]=str(grdp_package_length-1)
        databuff[1]=str(BL_CMD_GET_RDP_STATUS)
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
        if(int(bl_rep[1])==170):
            print("RDP level is 0")
    elif opt==5:
        gaddress_package_length=10
        databuff[0]=str(gaddress_package_length-1)
        databuff[1]=str(BL_CMD_GO_TO_ADDR)
        adress=input('Enter the adress')
        adress=int(adress,16)
        databuff[2]=word_to_byte(adress,1,1)
        databuff[3]=word_to_byte(adress,2,1)
        databuff[4]=word_to_byte(adress,3,1)
        databuff[5]=word_to_byte(adress,4,1)
        crc32 = get_crc(databuff[0:6],6)
        crc32 = crc32 & 0xffffffff
        databuff[6] = word_to_byte(crc32,1,1)
        databuff[7] = word_to_byte(crc32,2,1)
        databuff[8] = word_to_byte(crc32,3,1)
        databuff[9] = word_to_byte(crc32,4,1)
        write_to_ser(int(databuff[0]))
        for i_byte in databuff[1:10]:
            write_to_ser(int(i_byte))
        bl_rep=read_knowledge()
        print(bl_rep)
    elif opt==6:
        rflash_package_length=8
        databuff[0]=str(rflash_package_length-1)
        databuff[1]=str(BL_CMD_FLASH_ERASE)
        databuff[2]=int(input("Enter Sector number"))
        databuff[3]=int(input("number of Sectors"))
        crc32 = get_crc(databuff[0:4],4)
        crc32 = crc32 & 0xffffffff
        databuff[4] = word_to_byte(crc32,1,1)
        databuff[5] = word_to_byte(crc32,2,1)
        databuff[6] = word_to_byte(crc32,3,1)
        databuff[7] = word_to_byte(crc32,4,1)
        write_to_ser(int(databuff[0]))
        for i_byte in databuff[1:8]:
            write_to_ser(int(i_byte))
        bl_rep=read_knowledge()
        print(bl_rep)
    elif opt==7:
        f=open("test_bootloader.bin","rb")
        baseaddr=int(input('Enter Base adress to write Bin file'),16)
        j=0
        while True:
            databuff=[]
            for i in range(150):
                databuff.append(0)
            s=bytearray(f.read(100))
            if not s:
                break
            payload_len=len(s)
            length_of_package=(11+payload_len)
            databuff[0]=str(length_of_package-1)
            databuff[1]=str(BL_CMD_MEM_WRITE)
            # print(baseaddr)
            databuff[2]=word_to_byte(baseaddr,1,1)
            databuff[3]=word_to_byte(baseaddr,2,1)
            databuff[4]=word_to_byte(baseaddr,3,1)
            databuff[5]=word_to_byte(baseaddr,4,1)
            databuff[6]=payload_len
            baseaddr+=payload_len
            for i in range(payload_len):
                databuff[7+i]=s[i]
            bb=databuff[7:payload_len+7]
            crc32       = get_crc(bb,payload_len)
            crc32 = crc32 & 0xffffffff
            databuff[7+payload_len] = word_to_byte(crc32,1,1)
            databuff[8+payload_len] = word_to_byte(crc32,2,1)
            databuff[9+payload_len] = word_to_byte(crc32,3,1)
            databuff[10+payload_len] = word_to_byte(crc32,4,1)
            write_to_ser(int(databuff[0]))
            for i_byte in databuff[1:length_of_package]:
                write_to_ser(int(i_byte))
            rep_n=str(ser.readline()).split('-')
            print(rep_n,j)
            j+=1
            time.sleep(0.2)
            # if len(rep_n)>1:
            #     print("Ack is recevived",rep_n)

    else:
        print("Unrecognized command")
    databuff=[]
ser.close()



