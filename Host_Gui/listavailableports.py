import sys
import serial
import glob

def avaliable_ports():
    if sys.platform.startswith("win"):
        ports=['COM%s' % (i+1) for i in range(256)]
    elif sys.platform.startswith("linux"):
        ports=glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith("darwin"):
        ports=glob.glob("/dev/tty.*")
    else:
        raise EnvironmentError("Unsupported platform")
    av_ports=[]
    for port in ports:
        try:
            s=serial.Serial(port)
            s.close()
            av_ports.append(port)
        except (OSError,serial.SerialException):
            pass
    return av_ports

