import serial
import re
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading

# Configuración
ser = serial.Serial('COM3', 9600, timeout=2)  # Cambia 'COM3' al puerto correcto
MAX_LEN = 50  # Número de puntos mostrados en la gráfica

# Inicialización de listas para datos MPU y diccionario RSSI/MAC
gx_data, gy_data, gz_data = [], [], []
ax_data, ay_data, az_data = [], [], []
rssi = 0
mac_dict = {}

# Función para calcular distancia estimada a partir del RSSI
def calcular_distancia(rssi, tx_power=-59, n=2):
    return 10 ** ((tx_power - rssi) / (10 * n))

# Función para leer datos seriales en segundo hilo
def leer_datos_serial():
    global gx_data, gy_data, gz_data, ax_data, ay_data, az_data, rssi, mac_dict
    while True:
        try:
            linea = ser.readline().decode('utf-8', errors='ignore').strip()

            # Extraer RSSI y MAC
            if "RSSI" in linea and "MAC" in linea:
                match_red = re.search(r"RSSI:\s*(-?\d+), MAC:\s*([0-9a-f:]+)", linea, re.IGNORECASE)
                if match_red:
                    rssi = int(match_red.group(1))
                    mac = match_red.group(2)
                    mac_dict[mac] = rssi

            # Extraer datos MPU (acelerómetro y giroscopio)
            if "MPU:" in linea:
                match_mpu = re.search(
                    r'MPU:\s*AX:(-?\d+\.\d+),AY:(-?\d+\.\d+),AZ:(-?\d+\.\d+),GX:(-?\d+\.\d+),GY:(-?\d+\.\d+),GZ:(-?\d+\.\d+)', 
                    linea
                )
                if match_mpu:
                    ax, ay, az = map(float, match_mpu.group(1,2,3))
                    gx, gy, gz = map(float, match_mpu.group(4,5,6))

                    ax_data.append(ax)
                    ay_data.append(ay)
                    az_data.append(az)
                    gx_data.append(gx)
                    gy_data.append(gy)
                    gz_data.append(gz)

                    if len(ax_data) > MAX_LEN:
                        ax_data.pop(0)
                        ay_data.pop(0)
                        az_data.pop(0)
                        gx_data.pop(0)
                        gy_data.pop(0)
                        gz_data.pop(0)

        except Exception as e:
            print(f"Error leyendo datos: {e}")

# Crear ventanas para gráficos y tabla
fig_gyro, ax_gyro = plt.subplots()
fig_accel, ax_accel = plt.subplots()
fig_tabla, ax_tabla = plt.subplots()
fig_gyro.canvas.manager.set_window_title("Giroscopio")
fig_accel.canvas.manager.set_window_title("Acelerómetro")
fig_tabla.canvas.manager.set_window_title("Tabla de Dispositivos")

# Función para actualizar gráfico giroscopio
def actualizar_giroscopio(i):
    ax_gyro.clear()
    ax_gyro.plot(gx_data, label='GX')
    ax_gyro.plot(gy_data, label='GY')
    ax_gyro.plot(gz_data, label='GZ')
    ax_gyro.set_title("Giroscopio (°/s)")
    ax_gyro.set_ylim(-250, 250)
    ax_gyro.grid(True)
    ax_gyro.legend(loc='upper right')

# Función para actualizar gráfico acelerómetro
def actualizar_acelerometro(i):
    ax_accel.clear()
    ax_accel.plot(ax_data, label='AX')
    ax_accel.plot(ay_data, label='AY')
    ax_accel.plot(az_data, label='AZ')
    ax_accel.set_title("Acelerómetro (g)")
    ax_accel.set_ylim(-2, 2)
    ax_accel.grid(True)
    ax_accel.legend(loc='upper right')

# Función para actualizar tabla de dispositivos con RSSI y distancia
def actualizar_tabla(i):
    ax_tabla.clear()
    ax_tabla.axis('tight')
    ax_tabla.axis('off')

    distancia_dict = {mac: calcular_distancia(rssi) for mac, rssi in mac_dict.items()}
    tabla = [["N°", "MAC", "RSSI", "Distancia (m)"]]

    for i, (mac, rssi) in enumerate(mac_dict.items(), start=1):
        tabla.append([i, mac, rssi, round(distancia_dict[mac], 2)])

    t = ax_tabla.table(cellText=tabla, loc='center', cellLoc='center')
    t.scale(1, 2)

# Configurar animaciones de matplotlib
ani1 = FuncAnimation(fig_gyro, actualizar_giroscopio, interval=500)
ani2 = FuncAnimation(fig_accel, actualizar_acelerometro, interval=500)
ani3 = FuncAnimation(fig_tabla, actualizar_tabla, interval=1000)

# Iniciar hilo para lectura serial en background
thread = threading.Thread(target=leer_datos_serial, daemon=True)
thread.start()

# Mostrar ventanas
plt.show()