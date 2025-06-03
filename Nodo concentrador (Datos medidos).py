import serial
import threading
import re
import tkinter as tk
from tkinter import ttk
from collections import deque
import math
import numpy as np
from scipy.optimize import least_squares

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# CONFIGURA TU PUERTO SERIAL AQUÍ
SERIAL_PORT = 'COM7'
BAUD_RATE = 115200
MAX_POINTS = 100

# Coordenadas fijas para los nodos (x, y) en metros
fixed_nodes = {
    '28:cd:c1:06:5e:fd:': (0, 0),
    '28:cd:c1:06:5f:f9:': (10, 0),
    '28:cd:c1:06:4c:bb:': (0, 10),
    '28:cd:c1:06:5f:05:': (10, 10)   
    
}

data = {}

def rssi_to_distance(rssi, tx_power=-59, n=3.0):
    return round(10 ** ((tx_power - rssi) / (10 * n)), 2)

def error_trilateracion(estimacion, posiciones, distancias_reales, pesos):
    x_est, y_est = estimacion
    distancias_estimadas = []

    for (x, y), distancia_real, peso in zip(posiciones, distancias_reales, pesos):
        dist = np.sqrt((x_est - x) ** 2 + (y_est - y) ** 2)
        distancias_estimadas.append(dist * peso)
    
    return np.array(distancias_estimadas) - np.array(distancias_reales)

def trilateracion_optimized(positions, distances, rssi_values):
    max_rssi = max(rssi_values)
    pesos = [(max_rssi / rssi) for rssi in rssi_values]
    inicial = [0, 0]
    resultado = least_squares(error_trilateracion, inicial, args=(positions, distances, pesos))
    return resultado.x[0], resultado.x[1]

def parse_line_block(lines):
    mac, rssi = None, None
    ax = ay = az = gx = gy = gz = None

    for line in lines:
        if "Datos recibidos de" in line:
            mac = line.split("de")[1].strip()
        elif "RSSI:" in line and "Acelerómetro" not in line:
            match = re.search(r'RSSI:\s*(-?\d+)', line)
            if match:
                rssi = int(match.group(1))
        elif "Acelerómetro" in line:
            match = re.search(r'ax=([-.\d]+), ay=([-.\d]+), az=([-.\d]+)', line)
            if match:
                ax, ay, az = float(match.group(1)), float(match.group(2)), float(match.group(3))
        elif "Giroscopio" in line:
            match = re.search(r'gx=([-.\d]+), gy=([-.\d]+), gz=([-.\d]+)', line)
            if match:
                gx, gy, gz = float(match.group(1)), float(match.group(2)), float(match.group(3))

    return mac, rssi, ax, ay, az, gx, gy, gz

def serial_listener():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"📡 Escuchando en {SERIAL_PORT}...")
        block = []

        while True:
            line = ser.readline().decode(errors='ignore').strip()
            if line == "----------------------------------------":
                mac, rssi, ax, ay, az, gx, gy, gz = parse_line_block(block)
                block = []

                if mac and rssi is not None:
                    if mac not in data:
                        data[mac] = {
                            'rssi': rssi,
                            'distance': rssi_to_distance(rssi),
                            'accel_x': deque(maxlen=MAX_POINTS),
                            'accel_y': deque(maxlen=MAX_POINTS),
                            'accel_z': deque(maxlen=MAX_POINTS),
                            'gyro_x': deque(maxlen=MAX_POINTS),
                            'gyro_y': deque(maxlen=MAX_POINTS),
                            'gyro_z': deque(maxlen=MAX_POINTS),
                        }

                    data[mac]['rssi'] = rssi
                    data[mac]['distance'] = rssi_to_distance(rssi)

                    if ax is not None:
                        data[mac]['accel_x'].append(ax)
                        data[mac]['accel_y'].append(ay)
                        data[mac]['accel_z'].append(az)

                    if gx is not None:
                        data[mac]['gyro_x'].append(gx)
                        data[mac]['gyro_y'].append(gy)
                        data[mac]['gyro_z'].append(gz)
            else:
                block.append(line)

    except Exception as e:
        print("❌ Error en lectura serial:", e)

class App(tk.Tk):
    def __init__(self):  # ✅ Constructor corregido
        super().__init__()
        self.title("Monitoreo de nodos")
        self.geometry("1000x700")
        self.create_widgets()
        self.update_gui()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=('MAC', 'RSSI', 'Distancia'), show='headings')
        self.tree.heading('MAC', text='MAC')
        self.tree.heading('RSSI', text='RSSI (dBm)')
        self.tree.heading('Distancia', text='Distancia (m)')
        self.tree.pack(side=tk.TOP, fill=tk.X)

        frame_plots = tk.Frame(self)
        frame_plots.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.fig_sensors, (self.ax_g, self.ax_a) = plt.subplots(2, 1, figsize=(5, 4))
        plt.tight_layout()
        self.ax_g.set_title('Giroscopio')
        self.ax_g.set_xlim(0, MAX_POINTS)
        self.ax_g.set_ylim(-250, 250)
        self.ax_g.grid(True)

        self.ax_a.set_title('Acelerómetro')
        self.ax_a.set_xlim(0, MAX_POINTS)
        self.ax_a.set_ylim(-3, 3)
        self.ax_a.grid(True)

        self.line_gx, = self.ax_g.plot([], [], label='Gx')
        self.line_gy, = self.ax_g.plot([], [], label='Gy')
        self.line_gz, = self.ax_g.plot([], [], label='Gz')
        self.ax_g.legend()

        self.line_ax, = self.ax_a.plot([], [], label='Ax')
        self.line_ay, = self.ax_a.plot([], [], label='Ay')
        self.line_az, = self.ax_a.plot([], [], label='Az')
        self.ax_a.legend()

        canvas_sensors = FigureCanvasTkAgg(self.fig_sensors, master=frame_plots)
        canvas_sensors.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas_sensors = canvas_sensors

        self.fig_trilat, self.ax_trilat = plt.subplots(figsize=(5, 4))
        self.ax_trilat.set_xlim(-1, 12)
        self.ax_trilat.set_ylim(-1, 12)
        self.ax_trilat.set_title("Trilateración")
        self.ax_trilat.grid(True)

        canvas_trilat = FigureCanvasTkAgg(self.fig_trilat, master=frame_plots)
        canvas_trilat.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.canvas_trilat = canvas_trilat

    def update_gui(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for mac in data:
            self.tree.insert('', tk.END, values=(mac, data[mac]['rssi'], data[mac]['distance']))

        if data:
            for mac, d in data.items():
                if len(d['gyro_x']) > 0 and len(d['accel_x']) > 0:
                    x = list(range(len(d['gyro_x'])))
                    self.line_gx.set_data(x, d['gyro_x'])
                    self.line_gy.set_data(x, d['gyro_y'])
                    self.line_gz.set_data(x, d['gyro_z'])
                    self.line_ax.set_data(x, d['accel_x'])
                    self.line_ay.set_data(x, d['accel_y'])
                    self.line_az.set_data(x, d['accel_z'])
                    self.ax_g.set_xlim(0, MAX_POINTS)
                    self.ax_a.set_xlim(0, MAX_POINTS)
                    self.canvas_sensors.draw()
                    break

        self.ax_trilat.clear()
        self.ax_trilat.set_xlim(-1, 12)
        self.ax_trilat.set_ylim(-1, 12)
        self.ax_trilat.set_title("Trilateración (Ubicación estimada del nodo móvil)")
        self.ax_trilat.grid(True)

        positions = []
        distances = []
        rssi_values = []

        for mac, (x, y) in fixed_nodes.items():
            self.ax_trilat.plot(x, y, 'ro')
            self.ax_trilat.text(x + 0.1, y + 0.1, mac)
            if mac in data and 'distance' in data[mac]:
                positions.append((x, y))
                distances.append(data[mac]['distance'])
                rssi_values.append(data[mac]['rssi'])

        if len(positions) >= 3:
            est_pos = trilateracion_optimized(positions, distances, rssi_values)
            if est_pos:
                x, y = est_pos
                self.ax_trilat.plot(x, y, 'bo')
                self.ax_trilat.text(x + 0.1, y + 0.1, 'Nodo Móvil')

        self.canvas_trilat.draw()
        self.after(1000, self.update_gui)

# ✅ PUNTO DE ENTRADA
if __name__ == "__main__":
    threading.Thread(target=serial_listener, daemon=True).start()
    app = App()
    app.mainloop()
