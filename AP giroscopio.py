import network
import socket
import select
import time
from imu import MPU6050
from machine import Pin, I2C

# 1. Configurar AP
ap = network.WLAN(network.AP_IF)
ap.config(essid="Pico_AP", password="12345678")
ap.active(True)
while not ap.active():
    time.sleep(1)
print("📶 AP activo en:", ap.ifconfig()[0])

# 2. Inicializar MPU6050
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
imu = MPU6050(i2c)

# 3. Socket para recibir de transmisores
rx_socket = socket.socket()
rx_socket.bind(('0.0.0.0', 80))
rx_socket.listen(4)  # permitir hasta 4 transmisores
rx_socket.setblocking(False)

clients = []

# 4. Socket para recibir conexión del destino
tx_listener = socket.socket()
tx_listener.bind(('0.0.0.0', 8080))
tx_listener.listen(1)
tx_listener.setblocking(False)

dest_sock = None
print("⏳ Esperando conexión de RPi #3 (Destino)...")

while dest_sock is None:
    try:
        dest_sock, dest_addr = tx_listener.accept()
        dest_sock.setblocking(False)
        print("🔗 Conectado con RPi #3 desde:", dest_addr)
    except:
        time.sleep(1)

print("✅ Listo para recibir transmisores y reenviar datos")

# --- Esperar conexiones de transmisores por 10 segundos ---
WAIT_TIME = 20
print(f"⏳ Esperando {WAIT_TIME} segundos para que se conecten transmisores...")
start_wait = time.time()
while time.time() - start_wait < WAIT_TIME:
    try:
        client_sock, client_addr = rx_socket.accept()
        client_sock.setblocking(False)
        clients.append((client_sock, client_addr))
        print("📲 Transmisor conectado:", client_addr)
    except:
        pass
    time.sleep(0.1)

print("✅ Tiempo de espera terminado, iniciando bucle principal")

# 5. Bucle principal
while True:
    # Intentar aceptar nuevos transmisores incluso después del wait
    try:
        client_sock, client_addr = rx_socket.accept()
        client_sock.setblocking(False)
        clients.append((client_sock, client_addr))
        print("📲 Nuevo transmisor conectado:", client_addr)
    except:
        pass

    # Leer datos del MPU6050
    ax = round(imu.accel.x, 2)
    ay = round(imu.accel.y, 2)
    az = round(imu.accel.z, 2)
    gx = round(imu.gyro.x, 2)
    gy = round(imu.gyro.y, 2)
    gz = round(imu.gyro.z, 2)
    local_data = f"AX:{ax},AY:{ay},AZ:{az},GX:{gx},GY:{gy},GZ:{gz}"

    # Leer datos de los transmisores
    if clients:
        rlist, _, _ = select.select([s for s, _ in clients], [], [], 0.1)
        for sock in rlist:
            try:
                data = sock.recv(1024)
                if data:
                    msg = data.decode().strip()
                    addr = next(addr for s, addr in clients if s == sock)
                    print(f"📡 Recibido de {addr}: {msg}")

                    # Combinar datos
                    full_message = f"{msg} | MPU: {local_data}"
                    print("➡ Reenviando a RPi #3:", full_message)
                    dest_sock.send(full_message.encode())
                else:
                    clients = [(s, a) for s, a in clients if s != sock]
                    sock.close()
            except:
                pass

    time.sleep(0.5)
