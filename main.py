import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from db import setup_database
from scanner import read_serial, scancomports
from flask_server import run_flask_server

def start_server(port=8000):
    handler = SimpleHTTPRequestHandler
    httpd = TCPServer(("", port), handler)
    print(f"Serving at http://localhost:{port}")
    webbrowser.open(f'http://localhost:{port}')
    httpd.serve_forever()

def main():
    setup_database()
    ports = scancomports()
    threads = [threading.Thread(target=read_serial, args=(port, 9600)) for port in ports]
    threads.append(threading.Thread(target=run_flask_server))
    
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
