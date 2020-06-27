import serial
import struct

ser = serial.Serial('COM5', 115200, timeout=0,parity=serial.PARITY_NONE, rtscts=1)

CMD_GET_VERSION =0x51


def word_to_byte(addr, index , lowerfirst):
    value = (addr >> ( 8 * ( index -1)) & 0x000000FF )
    return value

def get_crc(buff, length):
    Crc = 0xFFFFFFFF
    #print(length)
    for data in buff[0:length]:
        Crc = Crc ^ data
        for i in range(32):
            if(Crc & 0x80000000):
                Crc = (Crc << 1) ^ 0x04C11DB7
            else:
                Crc = (Crc << 1)
    return Crc
def write_to_serial(value):
    if type(value)==int:
        data = struct.pack('>B', value)
    else:
        data = struct.pack('>B', ord(value))
        
    ser.write(data)

def read_knowledge():
    rep_n=str(ser.readline()).split('-')
    if len(rep_n)>1:
        if int(rep_n[1])==127:
            print("Nacknowledge is received")
        else:
            print("Ackowledge is Received")
            print(ser.readline().decode('utf-8'))
    else:
        print("Unsuccesfull reading")

databuff=[]
while True:
    
    for i in range(255):
        databuff.append(0)
    print("----------------------------\n")
    print("- For getting version : 1  -\n")
    print("----------------------------\n")
    opt=int(input('Enter option : '))
    if opt == 0:
        break
    elif opt==1:
        gv_package_length=6
        databuff[0:2]=b'5Q'
        crc32       = get_crc(databuff[0:2],2)
        crc32 = crc32 & 0xffffffff
        databuff[2] = chr(word_to_byte(crc32,1,1))
        databuff[3] = chr(word_to_byte(crc32,2,1))
        databuff[4] = chr(word_to_byte(crc32,3,1))
        databuff[5] = chr(word_to_byte(crc32,4,1))
        write_to_serial(databuff[0])
        for i_byte in databuff[1:6]:
            write_to_serial(i_byte)
        read_knowledge()
        
    else:
        print("Unrecognized command")
ser.close()



