import serial
import sys
from db import add_beer_for_person


def scancomports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = ['/dev/ttyS%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('darwin'):
        ports = ['/dev/tty.usbserial-%s' % (i + 1) for i in range(256)]
    else:
        raise EnvironmentError('Unsupported platform')

    print("Scanning for COM ports...")
    foundports = []

    for port in ports:
        try:
            ser = serial.Serial(port)
            ser.close()
            foundports.append(port)
            print(f"Found port: {port}")
        except (OSError, serial.SerialException):
            pass

    return foundports

def read_serial(port, baud_rate):
    try:
        ser = serial.Serial(port, baud_rate)
        while True:
            try:
                print(f"\nWaiting for barcode scan on {port}...")
                barcode_bytes = ser.readline().strip()
                barcode = barcode_bytes.decode('utf-8')
                barcode = barcode.replace("  ", " ")
                print(f"Scanned barcode on {port}: {barcode}")
                add_beer_for_person(barcode)
            except:
                print(f"{port} konnte nicht gelesen werden")    
    except:
        print(f"{port} konnte nicht geöffnet werden")
       


if __name__ == "__main__":
    scancomports()
