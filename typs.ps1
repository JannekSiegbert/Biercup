# Funktion zum Auflisten aller verfügbaren COM-Ports
function Get-AvailableComPorts {
    try {
        $ports = [System.IO.Ports.SerialPort]::GetPortNames()
        if ($ports.Length -eq 0) {
            Write-Host "Keine COM-Ports verfügbar."
        }
        return $ports
    } catch {
        Write-Host "Fehler beim Abrufen der COM-Ports: $_"
        return @()
    }
}

# Funktion zum Überprüfen, ob ein Port von einem Prozess verwendet wird
function Check-PortInUse {
    param (
        [string]$port
    )

    $portNumber = $port -replace 'COM', ''
    $connections = Get-NetTCPConnection | Where-Object { $_.LocalPort -eq $portNumber }
    
    if ($connections) {
        $pidlong = $connections.OwningProcess
        $process = Get-Process -Id $pidlong -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "Port $port wird von Prozess $($process.ProcessName) (PID: $pidlong) verwendet."
            return $pidlong
        }
    }

    return $null
}

# Funktion zum Beenden eines Prozesses
function Terminate-Process {
    param (
        [int]$pidlong
    )
    
    try {
        Stop-Process -Id $pidlong -Force
        Write-Host "Prozess mit PID $pidlong erfolgreich beendet."
    } catch {
        Write-Host "Fehler beim Beenden des Prozesses: $_"
    }
}

# Funktion zum Testen der Verbindung mit einem COM-Port
function Test-ComPort {
    param (
        [string]$comPort
    )

    try {
        $port = New-Object System.IO.Ports.SerialPort $comPort, 9600, None, 8, One
        $port.Open()
        Write-Host "Erfolgreich mit $comPort verbunden."
        $port.Close()
    } catch {
        Write-Host "Fehler beim Öffnen von $comPort $_"
    }
}

# Hauptlogik
function Main {
    # Liste verfügbare COM-Ports auf
    $availablePorts = Get-AvailableComPorts
    if ($availablePorts.Length -eq 0) {
        Write-Host "Keine verfügbaren COM-Ports gefunden. Beende das Programm."
        return
    }

    Write-Host "Verfügbare COM-Ports: $availablePorts"
    
    # Verwende den ersten verfügbaren COM-Port
    $selectedPort = $availablePorts
    $availablePorts | fl
    Write-Host "Versuche, COM-Port $selectedPort zu verbinden."

    # Prüfe, ob der COM-Port von einem anderen Prozess verwendet wird
    $pidlong = Check-PortInUse -port $selectedPort
    if ($pidlong) {
        $userInput = Read-Host "Der COM-Port $selectedPort wird von einem anderen Programm verwendet (PID: $pidlong). Möchtest du den Prozess beenden? (y/n)"
        if ($userInput -eq 'y') {
            Terminate-Process -pid $pidlong
            Write-Host "Prozess beendet. Versuche erneut, den Port zu öffnen."
        } else {
            Write-Host "Beende das Programm, um manuelle Korrekturen vorzunehmen."
            return
        }
    } else {
        Write-Host "Port $selectedPort ist frei."
    }

    # Teste die Verbindung mit dem COM-Port
    Test-ComPort -comPort $selectedPort
}

# Starte das Programm
Main
