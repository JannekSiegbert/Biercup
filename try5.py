import serial
import serial.tools.list_ports
import psutil

def list_available_ports():
    # Liste alle verfügbaren COM-Ports auf
    ports = serial.tools.list_ports.comports()
    available_ports = [port.device for port in ports]
    if not available_ports:
        print("Keine COM-Ports verfügbar.")
    return available_ports

def check_port_in_use(port):
    # Prüfe, ob der COM-Port von einem anderen Programm verwendet wird
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        for conn in proc.info.get('connections', []):
            if conn.status == psutil.CONN_LISTEN and conn.laddr.port == port:
                print(f"Port {port} wird von Prozess {proc.info['name']} (PID: {proc.info['pid']}) verwendet.")
                return proc.info['pid']
    return None

def read_from_comport(com_port):
    try:
        # Öffne den seriellen Port mit einer Baudrate von 9600
        ser = serial.Serial(com_port, 9600, timeout=1)
        print(f"Verbunden mit {ser.portstr}")

        while True:
            if ser.in_waiting > 0:
                # Lese die Daten und dekodiere sie in lesbaren Text
                data = ser.readline().decode('utf-8').strip()
                print(f"Empfangene Daten: {data}")
    except serial.SerialException as e:
        print(f"Fehler beim Zugriff auf den COM-Port: {e}")
    except KeyboardInterrupt:
        print("Programm beendet.")
    finally:
        if ser.is_open:
            ser.close()

def main():
    # Liste alle verfügbaren COM-Ports auf
    available_ports = list_available_ports()
    
    if available_ports:
        print(f"Verfügbare COM-Ports: {available_ports}")
        # Wähle den ersten verfügbaren COM-Port
        com_port = available_ports[0]
        print(f"Versuche, COM-Port {com_port} zu verbinden.")

        # Prüfe, ob der COM-Port von einem anderen Prozess verwendet wird
        pid = check_port_in_use(8)  # Beispiel für COM8
        if pid:
            print(f"Der COM-Port {com_port} wird von einem anderen Programm verwendet (PID: {pid}).")
            # User-Interaktion zum Beenden des Prozesses (manuell)
            user_input = input(f"Möchtest du den Prozess mit PID {pid} beenden? (y/n): ")
            if user_input.lower() == 'y':
                psutil.Process(pid).terminate()
                print(f"Prozess {pid} beendet. Versuche erneut, den Port zu öffnen.")
            else:
                print("Beende das Programm, um manuelle Korrekturen vorzunehmen.")
                return
        else:
            print(f"Port {com_port} ist frei.")
        
        # Lese Daten vom COM-Port
        read_from_comport(com_port)
    else:
        print("Keine verfügbaren COM-Ports gefunden.")

if __name__ == "__main__":
    main()
