# transmitter.py

import network       # Módulo para la conexión Wi-Fi
import socket        # Para enviar datos a través de red (UDP)
import time          # Para usar retardos
import ubinascii     # Para obtener la dirección MAC en formato legible
import machine       # (No se usa directamente aquí, pero sirve para reinicios, manejo de pines, etc.)

# Configura tu red WiFi
SSID = 'motoe'                 # Nombre de la red Wi-Fi a la que te vas a conectar
PASSWORD = '123456789'         # Contraseña de la red Wi-Fi

# Dirección IP del receptor que recibirá los datos (por ejemplo, una Raspberry Pi)
RECEIVER_IP = '192.168.43.221'  # Cambia esto a la IP de tu dispositivo receptor
RECEIVER_PORT = 12345           # Puerto donde el receptor está escuchando

# Conexión a la red Wi-Fi
wlan = network.WLAN(network.STA_IF)  # Modo estación (cliente)
wlan.active(True)                    # Activa la interfaz Wi-Fi
wlan.connect(SSID, PASSWORD)         # Intenta conectarse con las credenciales dadas

# Espera hasta que se establezca la conexión Wi-Fi
while not wlan.isconnected():
    print("Conectando a WiFi...")    # Mensaje mientras intenta conectar
    time.sleep(1)                    # Espera 1 segundo antes de volver a comprobar

print("Conectado:", wlan.ifconfig())  # Muestra IP, máscara, gateway y DNS cuando conecta

# Obtiene la dirección MAC del dispositivo y la convierte a un formato legible (tipo a4:cf:12:3b:4d:5e)
mac = ubinascii.hexlify(wlan.config('mac'), ':').decode()

# Crea un socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bucle principal: envío de datos cada 0.5 segundos
while True:
    rssi = wlan.status('rssi')                # Obtiene la potencia de la señal Wi-Fi (RSSI) en dBm
    mensaje = f"{mac},{rssi}"                 # Crea un mensaje con la MAC y el RSSI separados por coma
    sock.sendto(mensaje.encode(), (RECEIVER_IP, RECEIVER_PORT))  # Envía el mensaje codificado al receptor
    print("Enviado:", mensaje)                # Muestra el mensaje enviado por consola
    time.sleep(0.5)                           # Espera medio segundo antes del siguiente envío

