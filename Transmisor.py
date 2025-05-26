from machine import Pin, SPI
from nrf24l01 import NRF24L01
import network
import utime
import sys
import _thread

# 1. Configuración WiFi
wifi_ssid = "iPhone de Juan"
wifi_password = "juan08112002"

wlan = network.WLAN(network.STA_IF) # indica que el dispositivo se comportará como cliente (no como punto de acceso)
wlan.active(True) #Se activa el módulo WiFi y se intenta conectar.
wlan.connect(wifi_ssid, wifi_password)

print("Conectando a WiFi...")
timeout = 10 # Tiempo máximo para conectar
start_time = utime.time()
while not wlan.isconnected():
    if utime.time() - start_time > timeout:
        print("Error: Tiempo de conexión excedido") #Si no lo logra, muestra error y termina el programa.
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
        spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16)) #Configura la comunicación SPI para controlar el módulo NRF24L01.
        csn = Pin(15, mode=Pin.OUT, value=1)
        ce = Pin(14, mode=Pin.OUT, value=0) #csn y ce son pines necesarios para el control del módulo.
        
        nrf = NRF24L01(spi, csn, ce, payload_size=32) #Se establece un payload de 32 bytes.
        nrf.open_tx_pipe(b"1Node") #Se abre un canal de transmisión (pipe)
        nrf.set_channel(85) #Se configura el canal 85 (frecuencia de 2.485 GHz).
        nrf.set_power_speed(power_level, 1) #Se define una potencia inicial (power_level = 0) y velocidad de transmisión (1 Mbps).    
        
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

def cambiar_potencia_manual(): #Se inicia un hilo para que el usuario pueda ingresar manualmente un nivel de potencia (de 0 a 3).
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

_thread.start_new_thread(cambiar_potencia_manual, ()) #Llama a set_transmit_power(level) para modificar la potencia del módulo en tiempo real sin detener el programa principal.

# 4. Bucle principal de transmisión
print("\n📡 Iniciando transmisión...")
while True:
    rssi = get_rssi() #Obtiene la intensidad de señal WiFi (RSSI). (-30 es excelente, -90 es muy débil).
    msg = f"{device_id}|RSSI:{rssi}" #Se crea un mensaje con el ID del dispositivo y su nivel RSSI actual

    for attempt in range(3):
        try:
            print(f"📨 Intento {attempt+1}: Enviando {msg}")
            nrf.stop_listening()
            result = nrf.send(msg.encode()) #Intenta enviar el mensaje hasta 3 veces usando el módulo NRF24L01.
            nrf.start_listening()

            if result:
                print("✅ ¡Envío exitoso!")
                break
            else:
                print("❌ Fallo en envío")
        except Exception as e:
            print(f"⚠ Error: {e}")
        utime.sleep(0.5)

    utime.sleep(1) #Espera un segundo antes de volver a hacer el siguiente envío.
