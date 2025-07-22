import serial
import sys

def scancomports():
    # Determine the range of COM ports to scan based on the operating system
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

    if foundports:
        print("\nAvailable COM ports:")
        for port in foundports:
            print(f"- {port}")
    else:
        print("No COM ports found.")

if __name__ == "__main__":
    scancomports()