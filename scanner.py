import serial
import sys
from db import add_beer_for_person
import serial.tools.list_ports


def scancomports():
    print("Scanning for COM ports...")
    foundports = []

    list_of_ports = search_for_ports()
    for port in list_of_ports:
        foundports.append(port.description)
        print(f"Found port: {port.description}")

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
       
def search_for_ports():
    list_of_ports = list(serial.tools.list_ports.comports())
    return list_of_ports

if __name__ == "__main__":
    scancomports()
