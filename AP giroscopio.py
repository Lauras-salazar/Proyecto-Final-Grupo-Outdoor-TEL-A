import network
import socket
import time
import ubinascii
from machine import I2C, Pin
from imu import MPU6050
from ssd1306 import SSD1306_I2C

# Configuración Wi-Fi
SSID = 'motoe'
PASSWORD = '123456789'
RECEIVER_IP = '192.168.43.221'
RECEIVER_PORT = 12345

# Inicializa I2C para MPU6050 en bus 0 (GP0 SDA, GP1 SCL)
i2c_mpu = I2C(0, scl=Pin(1), sda=Pin(0))
imu = MPU6050(i2c_mpu)

# Inicializa I2C para OLED en bus 1 (GP3 SCL, GP2 SDA)
i2c_oled = I2C(1, scl=Pin(3), sda=Pin(2))
oled = SSD1306_I2C(128, 64, i2c_oled)

# Conectar a Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
print("Conectando a WiFi...")
while not wlan.isconnected():
    time.sleep(1)
print("Conectado a WiFi. IP:", wlan.ifconfig()[0])

mac = ubinascii.hexlify(wlan.config('mac'), ':').decode()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    rssi = wlan.status('rssi')

    # Leer acelerómetro y giroscopio
    ax = round(imu.accel.x, 2)
    ay = round(imu.accel.y, 2)
    az = round(imu.accel.z, 2)
    gx = round(imu.gyro.x, 2)
    gy = round(imu.gyro.y, 2)
    gz = round(imu.gyro.z, 2)

    # Construir mensaje con MAC, RSSI, acelerómetro y giroscopio
    mensaje = f"{mac},{rssi},{ax},{ay},{az},{gx},{gy},{gz}"
    sock.sendto(mensaje.encode(), (RECEIVER_IP, RECEIVER_PORT))
    print("Enviado:", mensaje)

    # Mostrar en OLED (acelerómetro arriba, giroscopio abajo)
    oled.fill(0)
    oled.text("Acelerometro:", 0, 0)
    oled.text(f"x:{ax} y:{ay}", 0, 12)
    oled.text(f"z:{az}", 0, 24)
    oled.text("Girometro:", 0, 40)
    oled.text(f"x:{gx} y:{gy}", 0, 52)
    oled.text(f"z:{gz}", 0, 64)  # Nota: la pantalla es 64 px alto, puede cortarse aquí, ajustar si quieres
    oled.show()

    time.sleep(1.5)
