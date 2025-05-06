from machine import Pin, SPI, I2C
from nrf24l01 import NRF24L01
import utime
import sys
import ssd1306  # Asegúrate de tener esta librería en tu Raspberry Pi Pico W

# 0. Inicializar pantalla OLED
i2c = I2C(0, scl=Pin(1), sda=Pin(0))  # Pines I2C estándar
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

power_level = 3  # Nivel de recepción (no afecta a transmisión)

def mostrar_en_pantalla(linea1="", linea2="", linea3=""):
    oled.fill(0)
    oled.text(linea1, 0, 0)
    oled.text(linea2, 0, 10)
    oled.text(linea3, 0, 20)
    oled.show()

# 1. Configuración del NRF24L01
def init_radio():
    try:
        spi = SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
        csn = Pin(15, mode=Pin.OUT, value=1)
        ce = Pin(14, mode=Pin.OUT, value=0)

        nrf = NRF24L01(spi, csn, ce, payload_size=32)
        nrf.open_rx_pipe(1, b"1Node")
        nrf.set_channel(85)
        nrf.set_power_speed(power_level, 1)
        nrf.start_listening()

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
    if nrf.any():
        try:
            buf = nrf.recv()
            msg = buf.decode().strip()

            if "|" in msg:
                device_id, rssi_value = msg.split("|", 1)
                print(f"📩 De {device_id}: {rssi_value}")
                mostrar_en_pantalla(f"ID: {device_id}", rssi_value, f"Pot:{power_level}")
            else:
                print(f"📩 Mensaje no válido: {msg}")
                mostrar_en_pantalla("Mensaje inválido", msg[:16], "")

        except Exception as e:
            print(f"⚠ Error al recibir: {e}")
            mostrar_en_pantalla("ERROR", str(e)[:16], str(e)[16:])

    utime.sleep(0.1)