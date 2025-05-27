import network       # Módulo para configurar y manejar la conexión Wi-Fi
import socket        # Módulo para manejar conexiones de red (UDP/TCP)
import time          # Módulo para manejar retardos y tiempos

# --- Credenciales Wi-Fi ---
SSID = 'motoe'          # Nombre de la red Wi-Fi
PASSWORD = '123456789'  # Contraseña del Wi-Fi

# --- Configurar conexión Wi-Fi en modo estación ---
wlan = network.WLAN(network.STA_IF)  # Configura el modo cliente Wi-Fi
wlan.active(True)                    # Activa la interfaz Wi-Fi
wlan.connect(SSID, PASSWORD)         # Conecta al Wi-Fi

print("Conectando a WiFi...")
while not wlan.isconnected():        # Espera hasta que se conecte
    time.sleep(1)

print("Receptor conectado. IP:", wlan.ifconfig()[0])  # Imprime la IP asignada

# --- Configuración del servidor UDP ---
PORT = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Crea el socket tipo UDP
sock.bind(('0.0.0.0', PORT))  # Escucha en todas las interfaces de red, en el puerto 12345

print(f"Escuchando en puerto {PORT}...")

# Diccionario para almacenar información por dispositivo (usando MAC como clave)
dispositivos = {}

# --- Bucle principal para recibir y procesar mensajes ---
while True:
    data, addr = sock.recvfrom(1024)   # Espera recibir un mensaje UDP
    mensaje = data.decode().strip()    # Decodifica el mensaje recibido
    partes = mensaje.split(',')        # Separa los campos del mensaje

    if len(partes) == 2:
        # Mensaje simple: solo MAC y RSSI
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
        # Mensaje completo: MAC, RSSI, acelerómetro y giroscopio
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
        # Si el mensaje no tiene 2 ni 8 partes, no es reconocido
        print("Mensaje recibido con formato inesperado:", mensaje)

