import network
import socket
import time

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect("Pico_AP", "12345678")

while not wifi.isconnected():
    time.sleep(1)

print("✅ Conectado al AP")
print("📡 IP local:", wifi.ifconfig()[0])

time.sleep(5)

mac = ':'.join('{:02x}'.format(b) for b in wifi.config('mac'))

addr = socket.getaddrinfo("192.168.4.1", 80)[0][-1]
s = socket.socket()
s.connect(addr)

while True:
    rssi = wifi.status('rssi')
    message = f"RSSI: {rssi}, MAC: {mac}"
    print("📤 Enviando:", message)
    s.send(message.encode())
    time.sleep(2)