import network
import socket
import time

SSID = 'motoe'          # Cambia aquí
PASSWORD = '123456789'  # Cambia aquí

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Conectando a WiFi...")
while not wlan.isconnected():
    time.sleep(1)

print("Receptor conectado. IP:", wlan.ifconfig()[0])

PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', PORT))

print(f"Escuchando en puerto {PORT}...")

dispositivos = {}

while True:
    data, addr = sock.recvfrom(1024)
    mensaje = data.decode().strip()
    partes = mensaje.split(',')

    if len(partes) == 2:
        # Solo MAC y RSSI
        mac, rssi = partes
        dispositivos[mac] = {
            "rssi": int(rssi),
            "accel": None,
            "gyro": None
        }
        print(f"\nDatos recibidos de {mac}:")
        print(f"  RSSI: {dispositivos[mac]['rssi']} dBm")
        print("-" * 40)

    elif len(partes) == 8:
        # MAC, RSSI y datos MPU
        mac, rssi, ax, ay, az, gx, gy, gz = partes
        dispositivos[mac] = {
            "rssi": int(rssi),
            "accel": (float(ax), float(ay), float(az)),
            "gyro": (float(gx), float(gy), float(gz))
        }
        print(f"\nDatos recibidos de {mac}:")
        print(f"  RSSI: {dispositivos[mac]['rssi']} dBm")
        print(f"  Acelerómetro: ax={dispositivos[mac]['accel'][0]}, ay={dispositivos[mac]['accel'][1]}, az={dispositivos[mac]['accel'][2]}")
        print(f"  Giroscopio:   gx={dispositivos[mac]['gyro'][0]}, gy={dispositivos[mac]['gyro'][1]}, gz={dispositivos[mac]['gyro'][2]}")
        print("-" * 40)

    else:
        print("Mensaje recibido con formato inesperado:", mensaje)
