import network
import socket
import time

wifi = network.WLAN(network.STA_IF) #Crea un objeto Wi-Fi en modo estación (STA_IF), es decir, conectarse a una red existente.
wifi.active(True) #
wifi.connect("Pico_AP", "12345678") #Intenta conectarse al Access Point (AP) con SSID Pico_AP
while not wifi.isconnected():
    time.sleep(1) #Espera hasta que se establezca la conexión Wi-Fi

print("✅ Conectado al AP")
print("📡 IP local:", wifi.ifconfig()[0]) #Confirma que se ha conectado y muestra la IP local asignada

time.sleep(5) #Espera 5 segundos antes de continuar. Útil si el servidor no está listo de inmediato.

mac = ':'.join('{:02x}'.format(b) for b in wifi.config('mac')) #Convierte la dirección MAC binaria en una cadena legible

addr = socket.getaddrinfo("192.168.4.1", 80)[0][-1] #Obtiene la dirección IP y puerto del servidor al que se quiere conectar
s = socket.socket()
s.connect(addr) #Crea un socket TCP y se conecta al servidor en 192.168.4.1, puerto 80

while True:
    rssi = wifi.status('rssi') # Valor de potencia de señal (RSSI)
    message = f"RSSI: {rssi}, MAC: {mac}"  # Crea el mensaje
    print("📤 Enviando:", message)
    s.send(message.encode()) # Lo envía al servidor como bytes
    time.sleep(2) # Espera 2 segundos
