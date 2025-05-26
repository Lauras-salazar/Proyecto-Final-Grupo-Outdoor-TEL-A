import network
import socket
import time

sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect("Pico_AP", "12345678")

while not sta.isconnected():
    time.sleep(1)

print("✅ Conectado al AP:", sta.ifconfig()[0])

time.sleep(5)

server_ip = "192.168.4.1"
server_port = 8080

s = socket.socket()
s.connect((server_ip, server_port))
print("🔗 Conectado al AP (RPi #2)")

while True:
    try:
        data = s.recv(1024)
        if data:
            print("📥 Datos recibidos:", data.decode())
    except:
        pass