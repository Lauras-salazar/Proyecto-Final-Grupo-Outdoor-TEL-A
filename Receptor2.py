import network
import socket
import time 

sta = network.WLAN(network.STA_IF) #network.STA_IF: activa la interfaz WiFi en modo cliente (station)
sta.active(True)
sta.connect("Pico_AP", "12345678") #Se conecta a una red creado por un Raspberry Pi actuando como servidor

while not sta.isconnected():
    time.sleep(1) #Espera en un bucle hasta que el dispositivo esté conectado a la red WiFi

print("✅ Conectado al AP:", sta.ifconfig()[0]) #Muestra la dirección IP asignada al cliente cuando se conectó correctamente

time.sleep(5) # Espera 5 segundos antes de continuar. Esto ayuda a asegurar que la red esté lista antes de conectarse al servidor.
#Crea un socket TCP (socket.socket()).
server_ip = "192.168.4.1" #Intenta conectarse al servidor en la IP 192.168.4.1 y puerto 8080.
server_port = 8080

s = socket.socket()
s.connect((server_ip, server_port))
print("🔗 Conectado al AP (RPi #2)") #Imprime un mensaje cuando la conexión se ha logrado.
while True:
    try:
        data = s.recv(1024) #Intenta recibir hasta 1024 bytes de datos
        if data:
            print("📥 Datos recibidos:", data.decode()) # Si hay datos, los imprime en consola, decodificándolos como texto (.decode()).
    except:
        pass #Si ocurre algún error (como una desconexión temporal), el try/except evita que el programa se detenga (pass simplemente ignora el error).
