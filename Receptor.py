from machine import Pin, SPI, I2C
from nrf24l01 import NRF24L01
import utime
import sys
import ssd1306  # Asegúrate de tener esta librería en tu Raspberry Pi Pico W

# 0. Inicializar pantalla OLED
i2c = I2C(0, scl=Pin(1), sda=Pin(0))  # Pines I2C estándar
oled = ssd1306.SSD1306_I2C(128, 64, i2c) #Se crea una instancia de la pantalla OLED de 128×64 píxeles.

power_level = 3  # Nivel de recepción (no afecta a transmisión)

def mostrar_en_pantalla(linea1="", linea2="", linea3=""):
    oled.fill(0)
    oled.text(linea1, 0, 0)
    oled.text(linea2, 0, 10)
    oled.text(linea3, 0, 20)
    oled.show()                #La función auxiliar mostrar_en_pantalla(linea1, linea2, linea3) limpia la pantalla y escribe hasta tres líneas de texto

# 1. Configuración del NRF24L01
def init_radio():
    try:
        spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16)) #Inicializas SPI igual que en el transmisor (SCK=18, MOSI=19, MISO=16).
        csn = Pin(15, mode=Pin.OUT, value=1)
        ce = Pin(14, mode=Pin.OUT, value=0) # Los pines CSN (chip select) y CE (chip enable) controlan el módulo.

        nrf = NRF24L01(spi, csn, ce, payload_size=32) #Indicas un tamaño de paquete de 32 bytes
        nrf.open_rx_pipe(1, b"1Node") # Abre el pipe #1 con dirección "1Node", para escuchar lo que el transmisor manda
        nrf.set_channel(85) #Se ajusta al canal 85 (2.485 GHz), igual que el transmisor
        nrf.set_power_speed(power_level, 1) #Define la potencia de recepción (aunque no afecta el rango de escucha) y la velocidad a 1 Mbps
        nrf.start_listening() #Pone al módulo en modo receptor

        print("✅ Receptor inicializado")
        mostrar_en_pantalla("NRF24L01 Receptor", "Canal: 85", f"Pot:{power_level} Vel:1Mbps")
        return nrf
    except Exception as e:
        print(f"❌ Error al inicializar radio: {e}")
        mostrar_en_pantalla("ERROR RADIO", str(e)[:16], str(e)[16:])
        sys.exit()

nrf = init_radio()

# 2. Bucle principal de recepción
while True:
    if nrf.any(): #Comprueba si hay un paquete esperando
        try:
            buf = nrf.recv()  #Si lo hay, nrf.recv() lo lee y devuelve un bytes de hasta 32 B
            msg = buf.decode().strip() #Lo decodificas a cadena y quitas espacios con .strip()

            if "|" in msg:
                device_id, rssi_value = msg.split("|", 1) #la parte antes de la barra (“A1B2C3”).
                print(f"📩 De {device_id}: {rssi_value}") #la parte después (“RSSI:-56”).
                mostrar_en_pantalla(f"ID: {device_id}", rssi_value, f"Pot:{power_level}")
            else:
                print(f"📩 Mensaje no válido: {msg}")
                mostrar_en_pantalla("Mensaje inválido", msg[:16], "")

        except Exception as e:
            print(f"⚠ Error al recibir: {e}")
            mostrar_en_pantalla("ERROR", str(e)[:16], str(e)[16:])#Si ocurre cualquier excepción al recibir o al decodificar, la atrapas y muestras un “ERROR” parcialmente en la OLED para debugging.

    utime.sleep(0.1)
