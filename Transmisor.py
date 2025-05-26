from machine import Pin, SPI
from nrf24l01 import NRF24L01
import network
import utime
import sys
import _thread

# 1. Configuración WiFi
wifi_ssid = "iPhone de Juan"
wifi_password = "juan08112002"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi_ssid, wifi_password)

print("Conectando a WiFi...")
timeout = 10
start_time = utime.time()
while not wlan.isconnected():
    if utime.time() - start_time > timeout:
        print("Error: Tiempo de conexión excedido")
        sys.exit()
    utime.sleep(0.5)
print("WiFi conectado")

# Obtener ID del dispositivo a partir de la MAC
device_mac = wlan.config('mac')
device_id = ''.join('{:02X}'.format(b) for b in device_mac[-3:])  # Últimos 3 bytes, ej: 'A1B2C3'
print(f"🆔 ID del transmisor: {device_id}")

# 2. Configuración NRF24L01
power_level = 0

def init_radio():
    try:
        spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
        csn = Pin(15, mode=Pin.OUT, value=1)
        ce = Pin(14, mode=Pin.OUT, value=0)
        
        nrf = NRF24L01(spi, csn, ce, payload_size=32)
        nrf.open_tx_pipe(b"1Node")
        nrf.set_channel(85)
        nrf.set_power_speed(power_level, 1)
        
        print("Radio configurado correctamente")
        return nrf
    except Exception as e:
        print(f"Error al inicializar radio: {e}")
        sys.exit()

nrf = init_radio()

def set_transmit_power(level):
    global power_level
    if level in [0, 1, 2, 3]:
        print(f"\n🔄 Cambiando potencia... (solicitud: {level})")
        power_level = level
        nrf.set_power_speed(power_level, 1)
        utime.sleep(1)
        print(f"✅ Potencia actual: {power_level}")
    else:
        print("⚠ Error: Nivel inválido (0-3)")

def get_rssi():
    try:
        return wlan.status('rssi')
    except:
        return -99

def cambiar_potencia_manual():
    global power_level
    while True:
        try:
            nivel = input("\nIngrese nivel de potencia (0-3): ").strip()
            if nivel.isdigit():
                set_transmit_power(int(nivel))
            else:
                print("⚠ Ingresa un número válido (0-3)")
        except KeyboardInterrupt:
            print("\n🔴 Saliendo del ajuste manual...")
            sys.exit()

_thread.start_new_thread(cambiar_potencia_manual, ())

# 4. Bucle principal de transmisión
print("\n📡 Iniciando transmisión...")
while True:
    rssi = get_rssi()
    msg = f"{device_id}|RSSI:{rssi}"

    for attempt in range(3):
        try:
            print(f"📨 Intento {attempt+1}: Enviando {msg}")
            nrf.stop_listening()
            result = nrf.send(msg.encode())
            nrf.start_listening()

            if result:
                print("✅ ¡Envío exitoso!")
                break
            else:
                print("❌ Fallo en envío")
        except Exception as e:
            print(f"⚠ Error: {e}")
        utime.sleep(0.5)

    utime.sleep(1)
