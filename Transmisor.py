# transmitter.py

import network
import socket
import time
import ubinascii
import machine

# Configura tu red WiFi
SSID = 'motoe'
PASSWORD = '123456789'

# Dirección IP del receptor (cambia a la IP de tu Raspberry receptora)
RECEIVER_IP = '192.168.43.221'
RECEIVER_PORT = 12345

# Conexión WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

# Esperar conexión
while not wlan.isconnected():
    print("Conectando a WiFi...")
    time.sleep(1)

print("Conectado:", wlan.ifconfig())

# Obtener dirección MAC
mac = ubinascii.hexlify(wlan.config('mac'), ':').decode()

# Socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    rssi = wlan.status('rssi')  # Nivel de señal
    mensaje = f"{mac},{rssi}"
    sock.sendto(mensaje.encode(), (RECEIVER_IP, RECEIVER_PORT))
    print("Enviado:", mensaje)
    time.sleep(0.5)
