# Requisitos: PyQt5, pyqtgraph, pyserial

import sys
import json
import csv
import time
import os
from datetime import datetime
from collections import deque

from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
import serial
import serial.tools.list_ports


# --- Worker thread para lectura serial ---
class SerialReader(QtCore.QThread):
    data_received = QtCore.pyqtSignal(dict)
    connection_lost = QtCore.pyqtSignal()
    connection_established = QtCore.pyqtSignal()

    def __init__(self, port, baudrate=115200, parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate
        self._running = True
        self._ser = None

    def run(self):
        try:
            self._ser = serial.Serial(self.port, self.baudrate, timeout=1)
            self.connection_established.emit()
        except Exception as e:
            print("Error abriendo puerto:", e)
            self.connection_lost.emit()
            return

        # leer líneas
        while self._running:
            try:
                line = self._ser.readline().decode(errors='ignore').strip()
                if not line:
                    continue
                parsed = self.parse_line(line)
                if parsed:
                    self.data_received.emit(parsed)
            except serial.SerialException:
                # conexión perdida
                self.connection_lost.emit()
                break
            except Exception as e:
                # ignora parse errors pero imprime para debug
                print("Error leyendo/parsing:", e, "line:", repr(line))
                continue

        try:
            if self._ser and self._ser.is_open:
                self._ser.close()
        except:
            pass

    def stop(self):
        self._running = False
        self.wait(1000)

    def parse_line(self, line: str):
        """
        Intentamos 2 formatos:
        1) JSON: {"temp":25.3,"gps":{"alt":...},"imu":{...},"mq135":...}
        2) CSV: temp,alt,x,y,roll,pitch,yaw,mq135
        Devuelve diccionario estandarizado.
        """
        # intento JSON
        try:
            obj = json.loads(line)
            out = {}
            out['temp'] = obj.get('temp') if 'temp' in obj else None
            gps = obj.get('gps', {})
            out['alt'] = gps.get('alt') if isinstance(gps, dict) else None
            out['x'] = gps.get('x') if isinstance(gps, dict) else None
            out['y'] = gps.get('y') if isinstance(gps, dict) else None
            imu = obj.get('imu', {})
            out['roll'] = imu.get('roll') if isinstance(imu, dict) else None
            out['pitch'] = imu.get('pitch') if isinstance(imu, dict) else None
            out['yaw'] = imu.get('yaw') if isinstance(imu, dict) else None
            out['mq135'] = obj.get('mq135') if 'mq135' in obj else None
            out['timestamp'] = time.time()
            return out
        except Exception:
            pass

        # intento CSV
        try:
            parts = [p.strip() for p in line.split(',') if p.strip()!='']
            if len(parts) >= 8:
                t, alt, x, y, roll, pitch, yaw, mq = parts[:8]
                out = {
                    'temp': float(t),
                    'alt': float(alt),
                    'x': float(x),
                    'y': float(y),
                    'roll': float(roll),
                    'pitch': float(pitch),
                    'yaw': float(yaw),
                    'mq135': float(mq),
                    'timestamp': time.time()
                }
                return out
        except Exception:
            pass

        # no pudo parsear
        return None


# --- Interfaz principal ---
class MainWindow(QtWidgets.QMainWindow):
    # Ruta fija del logo en Windows (cambiar si es necesario)
    FIXED_LOGO_PATH = r"imagenes\Logo_SPACE.jpg"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitor de Cohete")
        self.resize(1100, 700)

        # intentar establecer icono de ventana desde la ruta fija
        if os.path.exists(self.FIXED_LOGO_PATH):
            try:
                icon = QtGui.QIcon(QtGui.QPixmap(self.FIXED_LOGO_PATH))
                self.setWindowIcon(icon)
            except Exception as e:
                print("No se pudo establecer el icono de la ventana:", e)
        else:
            print(f"Logo no encontrado en: {self.FIXED_LOGO_PATH}")

        # variables de datos
        self.temp_history = deque(maxlen=500)
        self.mq_history = deque(maxlen=500)
        self.time_history = deque(maxlen=500)

        self.current_serial_thread = None
        self.csv_file = None
        self.csv_writer = None
        self.csv_path = self.default_csv_path()

        # interfaz
        self.init_ui()

        # temporizador para refrescar plots
        self.plot_timer = QtCore.QTimer()
        self.plot_timer.setInterval(300)  # ms
        self.plot_timer.timeout.connect(self.update_plots)
        self.plot_timer.start()

    def default_csv_path(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"esp32_data_{ts}.csv"
        return os.path.abspath(fname)

    def init_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)
        header = QtWidgets.QHBoxLayout()
        layout.addLayout(header)

        # Logo fijo (no editable desde la UI)
        self.logo_label = QtWidgets.QLabel()
        self.logo_label.setFixedSize(140, 60)
        self.logo_label.setScaledContents(True)
        header.addWidget(self.logo_label)

        # cargar la imagen fija si existe
        if os.path.exists(self.FIXED_LOGO_PATH):
            pix = QtGui.QPixmap(self.FIXED_LOGO_PATH)
            if not pix.isNull():
                self.logo_label.setPixmap(pix)
        else:
            # si no existe, mostrar texto de aviso
            self.logo_label.setText("Logo no encontrado")
            self.logo_label.setAlignment(QtCore.Qt.AlignCenter)

        header.addStretch()

        # Puerto serial y conexión
        self.port_combo = QtWidgets.QComboBox()
        self.refresh_ports()
        header.addWidget(QtWidgets.QLabel("Puerto:"))
        header.addWidget(self.port_combo)

        self.baud_combo = QtWidgets.QComboBox()
        self.baud_combo.addItems(["9600","115200","57600","38400","74880"])
        self.baud_combo.setCurrentText("115200")
        header.addWidget(QtWidgets.QLabel("Baud:"))
        header.addWidget(self.baud_combo)

        refresh_btn = QtWidgets.QPushButton("Actualizar puertos")
        refresh_btn.clicked.connect(self.refresh_ports)
        header.addWidget(refresh_btn)

        self.connect_btn = QtWidgets.QPushButton("Conectar")
        self.connect_btn.clicked.connect(self.toggle_connection)
        header.addWidget(self.connect_btn)

        # Estado de conexión (verde/rojo)
        self.status_label = QtWidgets.QLabel("No conectado")
        self.set_status(False)
        self.status_label.setFixedWidth(140)
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        header.addWidget(self.status_label)

        # Contenido principal: izquierda gráficas, derecha datos numéricos
        main_h = QtWidgets.QHBoxLayout()
        layout.addLayout(main_h, stretch=1)

        # Panel izquierdo - gráficas
        left_v = QtWidgets.QVBoxLayout()
        main_h.addLayout(left_v, stretch=3)

        # Temperatura
        self.temp_plot = pg.PlotWidget(title="Temperatura (°C)")
        self.temp_plot.showGrid(x=True, y=True)
        self.temp_curve = self.temp_plot.plot(pen=None)
        left_v.addWidget(self.temp_plot, stretch=1)

        # MQ135
        self.mq_plot = pg.PlotWidget(title="MQ135 (valor bruto)")
        self.mq_plot.showGrid(x=True, y=True)
        self.mq_curve = self.mq_plot.plot(pen=None)
        left_v.addWidget(self.mq_plot, stretch=1)

        # Panel derecho - valores y controles
        right_v = QtWidgets.QVBoxLayout()
        main_h.addLayout(right_v, stretch=2)

        # GPS group
        gps_group = QtWidgets.QGroupBox("GPS - Coordenadas")
        gps_layout = QtWidgets.QFormLayout()
        gps_group.setLayout(gps_layout)
        self.alt_label = QtWidgets.QLabel("N/A")
        self.x_label = QtWidgets.QLabel("N/A")
        self.y_label = QtWidgets.QLabel("N/A")
        gps_layout.addRow("Altitud:", self.alt_label)
        gps_layout.addRow("X (lat):", self.x_label)
        gps_layout.addRow("Y (lon):", self.y_label)
        right_v.addWidget(gps_group)

        # IMU group
        imu_group = QtWidgets.QGroupBox("IMU - Orientación")
        imu_layout = QtWidgets.QFormLayout()
        imu_group.setLayout(imu_layout)
        self.roll_label = QtWidgets.QLabel("N/A")
        self.pitch_label = QtWidgets.QLabel("N/A")
        self.yaw_label = QtWidgets.QLabel("N/A")
        imu_layout.addRow("Roll:", self.roll_label)
        imu_layout.addRow("Pitch:", self.pitch_label)
        imu_layout.addRow("Yaw:", self.yaw_label)
        right_v.addWidget(imu_group)

        # Última lectura
        last_group = QtWidgets.QGroupBox("Última lectura")
        last_layout = QtWidgets.QFormLayout()
        last_group.setLayout(last_layout)
        self.last_time_label = QtWidgets.QLabel("N/A")
        self.last_temp_label = QtWidgets.QLabel("N/A")
        self.last_mq_label = QtWidgets.QLabel("N/A")
        last_layout.addRow("Timestamp:", self.last_time_label)
        last_layout.addRow("Temp:", self.last_temp_label)
        last_layout.addRow("MQ135:", self.last_mq_label)
        right_v.addWidget(last_group)

        # Guardado / Export
        save_h = QtWidgets.QHBoxLayout()
        self.export_path_label = QtWidgets.QLabel(self.csv_path)
        save_h.addWidget(self.export_path_label)
        export_btn = QtWidgets.QPushButton("Exportar como...")
        export_btn.clicked.connect(self.export_as)
        save_h.addWidget(export_btn)
        right_v.addLayout(save_h)

        # Botón para abrir carpeta destino
        open_folder_btn = QtWidgets.QPushButton("Abrir carpeta destino")
        open_folder_btn.clicked.connect(self.open_folder)
        right_v.addWidget(open_folder_btn)

        right_v.addStretch()

    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.port_combo.addItem(f"{p.device} - {p.description}", p.device)
        if self.port_combo.count() == 0:
            self.port_combo.addItem("No hay puertos", "")

    def toggle_connection(self):
        if self.current_serial_thread and self.current_serial_thread.isRunning():
            self.disconnect_serial()
        else:
            port = self.port_combo.currentData()
            if not port:
                QtWidgets.QMessageBox.warning(self, "Puerto", "Selecciona un puerto válido.")
                return
            baud = int(self.baud_combo.currentText())
            self.connect_serial(port, baud)

    def connect_serial(self, port, baud):
        # iniciar hilo
        self.current_serial_thread = SerialReader(port, baud)
        self.current_serial_thread.data_received.connect(self.on_data)
        self.current_serial_thread.connection_lost.connect(self.on_connection_lost)
        self.current_serial_thread.connection_established.connect(self.on_connection_ok)
        self.current_serial_thread.start()
        self.connect_btn.setText("Desconectar")
        self.set_status(False)  # hasta que confirme

        # preparar CSV si no existe
        try:
            first = not os.path.exists(self.csv_path)
            self.csv_file = open(self.csv_path, "a", newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.csv_file)
            if first:
                header = ['timestamp', 'iso_time', 'temp', 'alt', 'x', 'y', 'roll', 'pitch', 'yaw', 'mq135']
                self.csv_writer.writerow(header)
                self.csv_file.flush()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "CSV", f"No se pudo abrir archivo CSV: {e}")

    def disconnect_serial(self):
        if self.current_serial_thread:
            self.current_serial_thread.stop()
            self.current_serial_thread = None
        self.set_status(False)
        self.connect_btn.setText("Conectar")
        if self.csv_file:
            try:
                self.csv_file.close()
            except:
                pass
            self.csv_file = None
            self.csv_writer = None

    def on_connection_ok(self):
        self.set_status(True)

    def on_connection_lost(self):
        self.set_status(False)
        QtWidgets.QMessageBox.warning(self, "Conexión", "Conexión perdida o no se pudo abrir el puerto.")
        self.disconnect_serial()

    def set_status(self, connected: bool):
        if connected:
            self.status_label.setText("Conexión correcta")
            self.status_label.setStyleSheet("background-color: #2ecc71; color: black; border-radius:6px; padding:4px;")
        else:
            self.status_label.setText("No conectado")
            self.status_label.setStyleSheet("background-color: #e74c3c; color: white; border-radius:6px; padding:4px;")

    @QtCore.pyqtSlot(dict)
    def on_data(self, data):
        # actualizar histories
        ts = data.get('timestamp', time.time())
        self.time_history.append(ts)
        self.temp_history.append(data.get('temp') if data.get('temp') is not None else float('nan'))
        self.mq_history.append(data.get('mq135') if data.get('mq135') is not None else float('nan'))

        # actualizar labels
        self.last_time_label.setText(datetime.fromtimestamp(ts).isoformat(sep=' '))
        self.last_temp_label.setText(str(data.get('temp', 'N/A')))
        self.last_mq_label.setText(str(data.get('mq135', 'N/A')))

        self.alt_label.setText(str(data.get('alt', 'N/A')))
        self.x_label.setText(str(data.get('x', 'N/A')))
        self.y_label.setText(str(data.get('y', 'N/A')))

        self.roll_label.setText(str(data.get('roll', 'N/A')))
        self.pitch_label.setText(str(data.get('pitch', 'N/A')))
        self.yaw_label.setText(str(data.get('yaw', 'N/A')))

        # guardar en CSV
        if self.csv_writer:
            try:
                iso = datetime.fromtimestamp(ts).isoformat(sep=' ')
                row = [
                    ts, iso,
                    data.get('temp'),
                    data.get('alt'),
                    data.get('x'),
                    data.get('y'),
                    data.get('roll'),
                    data.get('pitch'),
                    data.get('yaw'),
                    data.get('mq135')
                ]
                self.csv_writer.writerow(row)
                self.csv_file.flush()
            except Exception as e:
                print("Error guardando CSV:", e)

    def update_plots(self):
        # actualizar temperatura
        if len(self.time_history) > 0:
            x = [t - self.time_history[0] for t in self.time_history]
            y_temp = list(self.temp_history)
            y_mq = list(self.mq_history)
            try:
                self.temp_curve.setData(x, y_temp)
                self.mq_curve.setData(x, y_mq)
            except Exception as e:
                # evitar crash si los arrays contienen NaN o similares
                pass

    def export_as(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar datos como", self.csv_path, "CSV files (*.csv);;Text files (*.txt)")
        if not path:
            return
        # si archivo actual abierto, ciérralo y rename/copy
        try:
            # close current csv file if open
            if self.csv_file:
                self.csv_file.close()
                self.csv_file = None
                self.csv_writer = None
            # si existe el archivo temporal creado, simplemente renombrar/copy
            # si no existe (no se ha guardado nada), creamos con headers y vacio
            if os.path.exists(self.csv_path):
                # intenta copiar/renombrar
                try:
                    import shutil
                    shutil.copy(self.csv_path, path)
                except Exception as e:
                    # fallback: leer y escribir
                    with open(self.csv_path, 'r', encoding='utf-8') as r, open(path, 'w', encoding='utf-8') as w:
                        w.write(r.read())
            else:
                # crear archivo vacío con header
                with open(path, 'w', encoding='utf-8') as w:
                    w.write('timestamp,iso_time,temp,alt,x,y,roll,pitch,yaw,mq135\n')

            QtWidgets.QMessageBox.information(self, "Exportar", f"Datos exportados a:\n{path}")
            # actualizar ruta de csv actual para seguir guardando ahí
            self.csv_path = path
            self.export_path_label.setText(self.csv_path)
            # reabrir para append
            self.csv_file = open(self.csv_path, "a", newline='', encoding='utf-8')
            self.csv_writer = csv.writer(self.csv_file)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Exportar", f"Error exportando: {e}")

    def open_folder(self):
        folder = os.path.dirname(self.csv_path)
        if not os.path.exists(folder):
            QtWidgets.QMessageBox.warning(self, "Abrir carpeta", f"No existe la carpeta: {folder}")
            return
        # abrir carpeta (actualmente solo funciona para windows)
        if sys.platform.startswith('win'):
            os.startfile(folder)
        elif sys.platform.startswith('darwin'):
            QtCore.QProcess.startDetached("open", [folder])
        else:
            QtCore.QProcess.startDetached("xdg-open", [folder])

    def closeEvent(self, event):
        # limpiar hilo y archivos
        try:
            if self.current_serial_thread:
                self.current_serial_thread.stop()
        except:
            pass
        try:
            if self.csv_file:
                self.csv_file.close()
        except:
            pass
        event.accept()


def main():
    app = QtWidgets.QApplication(sys.argv)
    # estilo moderno básico
    QtWidgets.QApplication.setStyle("Fusion")
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
