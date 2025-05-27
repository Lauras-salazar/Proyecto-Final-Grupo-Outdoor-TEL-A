import network  # Importa el módulo para gestionar redes Wi-Fi (solo disponible en MicroPython)
import socket   # Importa el módulo para trabajar con conexiones de red mediante sockets
import time     # Importa el módulo para manejar tiempos y pausas

# Configura la interfaz Wi-Fi en modo estación (cliente)
wifi = network.WLAN(network.STA_IF)
wifi.active(True)  # Activa la interfaz Wi-Fi

# Conecta al punto de acceso con SSID "Pico_AP" y contraseña "12345678"
wifi.connect("Pico_AP", "12345678")

# Espera hasta que se logre la conexión Wi-Fi
while not wifi.isconnected():
    time.sleep(1)  # Espera 1 segundo antes de volver a comprobar

print("✅ Conectado al AP")  # Muestra mensaje de conexión exitosa
print("📡 IP local:", wifi.ifconfig()[0])  # Imprime la IP local asignada al dispositivo

time.sleep(5)  # Espera 5 segundos antes de continuar

# Obtiene la dirección MAC del dispositivo y la convierte a formato legible (xx:xx:xx:xx:xx:xx)
mac = ':'.join('{:02x}'.format(b) for b in wifi.config('mac'))

# Obtiene la dirección IP y puerto del servidor al que se va a conectar
addr = socket.getaddrinfo("192.168.4.1", 80)[0][-1]

# Crea un socket TCP/IP
s = socket.socket()
s.connect(addr)  # Conecta el socket al servidor

# Bucle infinito para enviar datos al servidor cada 2 segundos
while True:
    rssi = wifi.status('rssi')  # Obtiene la intensidad de la señal Wi-Fi (RSSI)
    message = f"RSSI: {rssi}, MAC: {mac}"  # Crea el mensaje con RSSI y MAC
    print("📤 Enviando:", message)  # Muestra el mensaje que se va a enviar
    s.send(message.encode())  # Envía el mensaje codificado por el socket
    time.sleep(2)  # Espera 2 segundos antes de enviar el siguiente mensaje

