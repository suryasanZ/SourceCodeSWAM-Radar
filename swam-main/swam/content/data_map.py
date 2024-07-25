import json
import csv
import os
import logging
import time
from PyQt5.QtWidgets import QWidget, QDateEdit, QLabel, QLineEdit, QFormLayout, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout, QTextEdit
from PyQt5.QtCore import QDateTime
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.ticker import FuncFormatter
from matplotlib.cm import ScalarMappable
from swam.addition import PopUpLevel, get_popup
from swam.content.worker import GPSWorker
from swam.content.worker import RadarWorker

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class DataMap(QWidget):
    def __init__(self):
        super().__init__()
        logging.debug("Inisialisasi DataMap")

        self.date_format = "dd-MM-yyyy"
        self.gps_worker = None
        self.radar_worker = None
        self.data_gps= []
        self.data_radar = []
        self.buffer = []

        
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDisplayFormat(self.date_format)
        self.date_input.setDateTime(QDateTime.currentDateTime())

        font_style = QFont()
        # font_style.setPointSize(12)  
        font_style.setFamily("Georgia")

        lbl_name = QLabel("Petugas:")
        lbl_name.setFont(font_style)
        lbl_loc = QLabel("Lokasi:")
        lbl_loc.setFont(font_style)
        lbl_date = QLabel("Tanggal:")
        lbl_date.setFont(font_style)

        self.txt_name = QLineEdit()
        self.txt_loc = QLineEdit()
        self.txt_name.setFixedSize(200, 40)
        self.txt_loc.setFixedSize(200, 40)

        # Creating a form layout and adding widgets
        form_layout = QFormLayout()
        form_layout.addRow(lbl_name, self.txt_name)
        form_layout.addRow(lbl_loc, self.txt_loc)
        form_layout.addRow(lbl_date, self.date_input)

        self.btn_style= """
            QPushButton {
                border-radius: 5px; /* radius border dalam pixels */
                min-width: 85px; /* ukuran minimum lebar */
                min-height: 45px; /* ukuran minimum tinggi */
                font: 12pt 'Arial'; /* ukuran dan jenis font */
                padding: 5px; /* padding dalam tombol */
            }
            QPushButton:disabled {
                color: grey; /* warna teks saat tombol dinonaktifkan */
            }
            """

        self.btn_start_scan = QPushButton("Mulai\nDeteksi")
        self.btn_start_scan.setStyleSheet(self.btn_style)
        self.btn_start_scan.clicked.connect(self.start_scan)
        
        self.btn_stop_scan = QPushButton("Berhenti\nDeteksi")
        self.btn_stop_scan.setStyleSheet(self.btn_style)
        self.btn_stop_scan.setEnabled(False)
        self.btn_stop_scan.clicked.connect(self.stop_scan)

        self.btn_save_data = QPushButton("Simpan\nData")
        self.btn_save_data.setStyleSheet(self.btn_style)
        self.btn_save_data.clicked.connect(self.save_data)

        self.btn_reset = QPushButton("Reset\nData")
        self.btn_reset.setStyleSheet(self.btn_style)
        self.btn_reset.clicked.connect(self.reset_data)


        # Creating a vertical layout for buttons
        btn_layout = QGridLayout()
        btn_layout.addWidget(self.btn_start_scan, 0,0)
        btn_layout.addWidget(self.btn_stop_scan, 0,1)
        btn_layout.addWidget(self.btn_save_data, 0,2)
        btn_layout.addWidget(self.btn_reset, 0,3)

        self.box_style= """
            QPushButton { 
                border-radius: .5em;
                border: 2px solid #000;
                color: #000000;
                min-width: 205px;
                min-height: 65px;
                font: 24pt Arial;
                padding: 5px; /* padding dalam tombol */
            }

            """

        judul_box = QPushButton("Pemetaan KAT")
        judul_box.setStyleSheet(self.box_style)


        # Creating a horizontal layout to position the form layout at the top
        hbox_layout = QHBoxLayout()
        hbox_layout.addLayout(form_layout)
        hbox_layout.addLayout(btn_layout)
        hbox_layout.addStretch(4)  # Add stretch to push the form to the left
        # hbox_layout.addWidget(judul_box)
        # hbox_layout.addStretch(1)  # Add stretch to push the form to the left

        self.mv_label = QLabel("Kandungan Air Tanah:")
        # self.mv_label.setStyleSheet("font-family: Georgia;")
        self.mv_value = QLineEdit()
        self.mv_value_text = QLineEdit()
        self.mv_value_text.setReadOnly(True)
        self.mv_label.setFont(font_style)
        mv_layout = QHBoxLayout()
        mv_layout.addWidget(self.mv_label)
        mv_layout.addWidget(self.mv_value_text)

        self.coor_label = QLabel("Koordinat GPS:")
        # self.coor_label.setStyleSheet("font-family: Georgia;")
        self.coor_data = QLineEdit()
        self.coor_data.setReadOnly(True)
        self.coor_label.setFont(font_style)
        coor_layout = QHBoxLayout()
        coor_layout.addWidget(self.coor_label)
        coor_layout.addWidget(self.coor_data)

        value_layout = QGridLayout()
        value_layout.addLayout(coor_layout, 0,0)
        value_layout.addLayout(mv_layout, 0,1)

        # Setting the main vertical layout for the page
        main_layout = QVBoxLayout()
        main_layout.addLayout(hbox_layout)
        self.map_widget = MapPlotWidget()
        main_layout.addWidget(self.map_widget)

        # main_layout.addLayout(coor_layout)
        # main_layout.addLayout(mv_layout)
        main_layout.addLayout(value_layout)
        self.setLayout(main_layout)

    def start_scan(self):
        logging.debug("Menekan tombol Mulai Deteksi")
        # Load settings and initialize radar worker
        self.btn_start_scan.setEnabled(False)
        self.btn_stop_scan.setEnabled(True)

        device_port = load_setting(self)
        self.gps_port = str(device_port.get("gps_port"))
        self.radar_port = str(device_port.get("radar_port"))
        logging.debug(f"Radar port: {self.radar_port}, GPS Port: {self.gps_port}")


        # print(self.radar_port)
        if self.radar_worker is None:
            self.radar_worker = RadarWorker(self.radar_port)  
            self.radar_worker.data_radar.connect(self.update_radar)
            self.radar_worker.start()

        if self.gps_worker is None:
            self.gps_worker = GPSWorker(self.gps_port)  
            self.gps_worker.data_gps.connect(self.update_gps)
            self.gps_worker.start()
    

    def stop_scan(self):
        logging.debug("Menekan tombol Berhenti Deteksi")

        self.btn_start_scan.setEnabled(True)
        self.btn_stop_scan.setEnabled(False)
        if self.gps_worker is not None:
            self.gps_worker.stop()
            self.gps_worker.wait()
            self.gps_worker = None

        if self.radar_worker is not None:
            self.radar_worker.stop()
            self.radar_worker = None

    def update_radar(self, s21):
        mv_v = None  # Initialize mv_v to None

        if self.radar_worker is not None:
            mv, top_peaks = self.radar_worker.swc_calc(s21)

            if isinstance(mv, tuple):
                mv_v = mv[0]
            else:
                mv_v = mv

            # print(f"Radar Data Updated: Moisture Value: {mv_v}")

            if mv_v is not None:
                mv_value_text = f"{round(mv_v * 100, 3)}%"
                # print(f"Radar Data Updated: Moisture Value: {mv_v}")
                self.mv_value_text.setText(mv_value_text)
                self.data_radar.append(mv_v)
                self.mv_value.setText(f"{mv_v:.4f}")

        if self.data_gps and mv_v is not None:
            last_lat, last_lon = self.data_gps[-1]
            self.buffer.append((float(last_lat), float(last_lon), mv_v))
            self.map_widget.update_plot(float(last_lat), float(last_lon), mv_v)
        else:
            print("Data GPS or mv_v is not available for update_plot.")

    def update_gps(self, data):
        latitude, longitude = data
        self.data_gps.append(data)
        self.coor_data.setText(f"Latitude : {latitude}, Longitude : {longitude}")

        # print(f"GPS Data Updated: Latitude: {latitude}, Longitude: {longitude}")

        if self.data_gps and self.radar_worker is not None:
            last_mv = float(self.mv_value.text()) if self.mv_value.text() else 0
            self.map_widget.update_plot(float(latitude), float(longitude), last_mv)

    def save_data(self):
        logging.debug("Menekan tombol Simpan Data")
        txt_name_text = self.txt_name.text()
        txt_loc_text = self.txt_loc.text()
        txt_date_text = self.date_input.text()
        dir_gps = f"./swam/Penyimpanan_data/DataPemetaan/Data_Pemetaan_{txt_name_text}_{txt_loc_text}_{txt_date_text}.csv"
        os.makedirs(os.path.dirname(dir_gps), exist_ok=True)
        data_buffer = self.buffer

        if len(data_buffer) < 1 :
            get_popup("Tidak ada data, tidak bisa menyimpan", PopUpLevel.WARN)
            logging.warning("Tidak ada data untuk disimpan")


        else:
            with open(dir_gps, mode='w', newline='') as file_gps:
                writer = csv.writer(file_gps)
                writer.writerow(['latitude', 'longitude', 'swc_value']) 
                for latitude, longitude, swc  in data_buffer:
                    writer.writerow([latitude, longitude, swc])

            get_popup("Data pemetaan berhasil disimpan", PopUpLevel.INFO, self)
            logging.debug(f"Data sinyal terima telah disimpan pada directory {dir_gps}")

    
    def reset_data(self):
        logging.debug("Menekan tombol Reset Data")

        if len(self.data_radar or self.data_gps)<1:
            get_popup("Tidak ada data, tidak dapat reset data", PopUpLevel.WARN, )

        else:
            self.mv_value_text.setText("")
            self.coor_data.setText("")
            self.data_gps = []
            self.buffer = []
            self.map_widget.reset_plot()
            get_popup("Data telah direset kembali.", PopUpLevel.INFO, )
            logging.debug("Data telah dikosongkan dan hasil plot data telah dibersihkan kembali")


class MapPlotWidget(QWidget):
    def __init__(self, parent=None):
        super(MapPlotWidget, self).__init__(parent)

        self.figure = plt.figure(figsize=(5, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Longitude')
        self.ax.set_ylabel('Latitude')
        self.ax.set_title('Pemetaan Kandungan Air Tanah')
        self.ax.grid(True)

        # self.swc_cmap = self._create_swc_colormap()
        self.swc_cmap = plt.get_cmap('plasma_r')
        self.sm = ScalarMappable(cmap=self.swc_cmap)

        self.cbar = self.figure.colorbar(self.sm, ax=self.ax, orientation='vertical')
        def percentage(x, pos):
            return f'{x * 100:.0f}%'

        # Mengatur format keterangan tick
        self.cbar.ax.yaxis.set_major_formatter(FuncFormatter(percentage))
        self.cbar.set_label('Kandungan Air Tanah (KAT)')

        self.buffer = []
        self.frame = 0

    def update_plot(self, latitude, longitude, swc_value):
        start_time = time.time()
        logging.debug("Mulai plotting data fitur Pemetaan KAT")
        self.buffer.append((latitude, longitude, swc_value))

        self.ax.clear()
        self.ax.set_xlabel('Longitude')
        self.ax.set_ylabel('Latitude')
        self.ax.set_title('Pemetaan Kandungan Air Tanah')
        self.ax.grid(True)

        for lat, lon, swc in self.buffer:
            self.ax.scatter(lon, lat, color=self.sm.to_rgba(swc))

        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.debug(f"Selesai plotting data dalam {elapsed_time:.2f} detik")


    def reset_plot(self):
        logging.debug("Reset plot")
        self.buffer = []
        self.ax.clear()
        self.ax.set_xlabel('Longitude')
        self.ax.set_ylabel('Latitude')
        self.ax.set_title('Pemetaan Kandungan Air Tanah')
        self.ax.grid(True)
        self.canvas.draw()

def load_setting(self) -> dict:

    file_path = "./swam/setting_data.json"
    try:
        with open(file_path, 'r') as file:
            return json.loads(file.read())

    except FileNotFoundError:
        return {}
    
