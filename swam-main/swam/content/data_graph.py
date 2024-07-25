from PyQt5.QtWidgets import QWidget, QDateEdit, QLabel, QLineEdit, QFormLayout, QPushButton, QHBoxLayout, QVBoxLayout, QRadioButton, QGridLayout
from PyQt5.QtCore import QDateTime
from PyQt5.QtGui import QFont
import json
import csv
import numpy as np
import os
import logging
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from .worker import RadarWorker
from swam.addition import PopUpLevel, get_popup

# Konfigurasi logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class DataGraph(QWidget):
    def __init__(self):
        super().__init__()
        logging.debug("Inisialisasi DataGraph")
        
        # Inisialisasi widgets dan layout...
        self.date_format = "dd-MM-yyyy"
        self.data_radar = []
        self.data_radar_RI = []
        self.data_raw = []

        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDisplayFormat(self.date_format)
        self.date_input.setDateTime(QDateTime.currentDateTime())

        font_style = QFont()
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

        form_layout = QFormLayout()
        form_layout.addRow(lbl_name, self.txt_name)
        form_layout.addRow(lbl_loc, self.txt_loc)
        form_layout.addRow(lbl_date, self.date_input)
        btn_layout = self._button_scan()

        self.box_style = """
            QPushButton { 
                border-radius: .5em;
                border: 2px solid #000;
                color: #000000;
                min-width: 205px;
                min-height: 65px;
                font: 24pt Arial;
                padding: 5px;
            }
        """

        judul_box = QPushButton("Grafik KAT")
        judul_box.setStyleSheet(self.box_style)

        hbox_layout = QHBoxLayout()
        hbox_layout.addLayout(form_layout)
        hbox_layout.addLayout(btn_layout)
        hbox_layout.addStretch(4)

        self.index_label = QLabel("Jarak :")
        self.index_label.setFont(font_style)
        self.index_value = QLineEdit()
        self.index_value.setReadOnly(True)
        self.index_value.setFont(font_style)
        index_layout = QHBoxLayout()
        index_layout.addWidget(self.index_label)
        index_layout.addWidget(self.index_value)

        self.ptp_label = QLabel("Nilai Peak-to-peak: ")
        self.ptp_label.setFont(font_style)
        self.ptp_value = QLineEdit()
        self.ptp_value.setReadOnly(True)
        self.ptp_value.setFont(font_style)
        ptp_layout = QHBoxLayout()
        ptp_layout.addWidget(self.ptp_label)
        ptp_layout.addWidget(self.ptp_value)

        self.mv_label = QLabel("Kandungan Air Tanah:")
        self.mv_label.setFont(font_style)
        self.mv_value = QLineEdit()
        self.mv_value.setReadOnly(True)
        self.mv_value.setFont(font_style)
        mv_layout = QHBoxLayout()
        mv_layout.addWidget(self.mv_label)
        mv_layout.addWidget(self.mv_value)

        value_layout = QGridLayout()
        value_layout.addLayout(index_layout, 0, 0)
        value_layout.addLayout(ptp_layout, 0, 1)
        value_layout.addLayout(mv_layout, 0, 2)

        main_layout = QVBoxLayout()
        main_layout.addLayout(hbox_layout)
        self.plot_canvas = PlotWidget(self)
        main_layout.addWidget(self.plot_canvas)
        main_layout.addLayout(value_layout)
        self.setLayout(main_layout)

    def _button_scan(self):
        logging.debug("Inisialisasi tombol scan")
        
        self.btn_style = """
            QPushButton {
                border-radius: 5px; 
                min-width: 85px; 
                min-height: 45px; 
                font: 12pt 'Arial'; 
                padding: 5px; 
            }
            QPushButton:disabled {
                color: grey; 
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

        btn_layout = QGridLayout()
        btn_layout.addWidget(self.btn_start_scan, 0, 0)
        btn_layout.addWidget(self.btn_stop_scan, 0, 1)
        btn_layout.addWidget(self.btn_save_data, 0, 2)
        btn_layout.addWidget(self.btn_reset, 0, 3)

        return btn_layout

    def start_scan(self):
        logging.debug("Menekan tombol Mulai Deteksi")
        
        self.btn_start_scan.setEnabled(False)
        self.btn_stop_scan.setEnabled(True)
        
        device_port = load_setting(self)
        self.radar_port = str(device_port.get("radar_port"))
        logging.debug(f"Radar port: {self.radar_port}")
        
        self.radar_worker = RadarWorker(self.radar_port)
        self.radar_worker.data_radar.connect(self.update_plot)
        self.radar_worker.data_RI.connect(self.update_RI)

        if not self.radar_worker.isRunning():
            self.radar_worker.start()

    def stop_scan(self):
        logging.debug("Menekan tombol Berhenti Deteksi")
        
        self.btn_start_scan.setEnabled(True)
        self.btn_stop_scan.setEnabled(False)
        
        if self.radar_worker.isRunning():
            self.radar_worker.stop()

    def save_data(self):
        logging.debug("Menekan tombol Simpan Data")
        
        name_text = self.txt_name.text()
        loc_text = self.txt_loc.text()
        date_text = self.date_input.text()
        dir_data_radar = f"./swam/Penyimpanan_data/DataSinyalPantul/DataStrec_{name_text}_{loc_text}_{date_text}.csv"
        dir_data_RI = f"./swam/Penyimpanan_data/DataRealImajiner/DataRI_{name_text}_{loc_text}_{date_text}.csv"
        data_radar = np.array(self.data_radar)
        data_RI = self.data_radar_RI
        os.makedirs(os.path.dirname(dir_data_radar), exist_ok=True)
        os.makedirs(os.path.dirname(dir_data_RI), exist_ok=True)

        if len(data_radar) < 1:
            get_popup("Tidak ada data, tidak dapat menyimpan!", PopUpLevel.WARN, self)
            logging.warning("Tidak ada data untuk disimpan")
        else:
            data_radar = [list(x) for x in data_radar]
            data_RI = [list(x) for x in data_RI]
            data_RI = [str(x).replace('(', '').replace(')', '') for x in data_RI]

            with open(dir_data_radar, mode='w', newline='') as file_radar:
                writer = csv.writer(file_radar, delimiter=";")
                for value in data_radar:
                    writer.writerow(value)
            logging.debug(f"Data sinyal terima telah disimpan pada directory {dir_data_radar}")

            with open(dir_data_RI, mode='w', newline='') as file_RI:
                writer = csv.writer(file_RI, delimiter=";")
                for value in data_RI:
                    writer.writerow([value])
            logging.debug(f"Data S21 Real+Imajiner telah disimpan pada directory {dir_data_RI}")

            get_popup("Data radar berhasil disimpan!", PopUpLevel.INFO, self)

    def reset_data(self):
        logging.debug("Menekan tombol Reset Data")

        if len(self.data_radar) < 1:
            get_popup("Tidak ada data, tidak dapat reset data!", PopUpLevel.INFO, self)
            logging.info("Tidak ada data untuk direset")
        else:
            self.mv_value.setText("")
            self.index_value.setText("")
            self.ptp_value.setText("")
            self.data_radar = []
            self.data_radar_RI = []
            self.plot_canvas.reset_plot()
            get_popup("Data telah direset kembali.", PopUpLevel.INFO, self)
            logging.debug("Data telah dikosongkan dan hasil plot data telah dibersihkan kembali")

    def update_RI(self, s21_RI):
        # logging.debug(f"Memperbarui data RI dengan nilai: {s21_RI}")
        self.data_radar_RI.append(s21_RI)

    def update_plot(self, s21):
        logging.debug(f"Memperbarui plot dengan nilai: {s21}")
        self.data_radar.append(s21)
        mv, top_peaks = self.radar_worker.swc_calc(s21)
        self.plot_canvas.plot(s21, top_peaks)
        mv_value_text = f"{round(mv * 100, 3)}%"
        self.mv_value.setText(mv_value_text)
        ratio = 25 / 24
        
        # Konversi runtun data ke jarak dalam centimeter
        jarak = [i * ratio for i in top_peaks]

        if len(top_peaks) > 1:  # PEAK TO PEAK 
            peak_value_text = f"{round(jarak[0], 2)} = {round(s21[top_peaks[0]], 3)}, {round(jarak[1], 2)} = {round(s21[top_peaks[1]], 3)}"
            self.ptp_value.setText(peak_value_text)           
        else:
            self.ptp_value.setText("Jarak Tidak dapat dihitung")            

        if len(jarak) > 0:  # JARAK CM
            jarak_text = f"{round(jarak[0], 2)} cm"
            self.index_value.setText(jarak_text)
        else:
            self.index_value.setText("Jarak Tidak dapat dihitung")

    def closeEvent(self, event):
        logging.debug("Menutup jendela DataGraph")
        self.stop_scan()
        event.accept()

class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super(PlotWidget, self).__init__(parent)
        logging.debug("Inisialisasi PlotWidget")

        self.figure = plt.figure(figsize=(5, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Jarak (cm)')
        self.ax.set_ylabel('Amplituda')
        self.ax.set_title('Hasil Deteksi Kandungan Air Tanah')
        self.ax.grid(True)

    def plot(self, Strec, top_peaks):
        start_time = time.time()
        logging.debug("Mulai plotting data Fitur Pemetaan KAT")

        # Mengubah garis datar menjadi jarak(cm)
        self.ax.clear()
        
        # Rasio konversi dari runtun ke jarak dalam centimeter
        ratio = 25 / 24
        
        # Konversi runtun data ke jarak dalam centimeter
        x_cm = [i * ratio for i in range(len(Strec))]
        top_peaks_cm = [i * ratio for i in top_peaks]

        # Plot data dengan sumbu x dalam centimeter
        self.ax.plot(x_cm, Strec, label='S21 Data')
        self.ax.plot(top_peaks_cm, [Strec[i] for i in top_peaks], "x", label='Top Peaks')
        
        self.ax.legend()
        self.ax.set_xlabel('Jarak (cm)')
        self.ax.set_ylabel('Amplituda')
        self.ax.set_title('Hasil Deteksi Kandungan Air Tanah')
        self.ax.grid(True)
        self.canvas.draw()

        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.debug(f"Selesai plotting data dalam {elapsed_time:.2f} detik")

    def reset_plot(self):
        logging.debug("Reset plot")
        
        self.ax.clear()
        self.ax.set_xlabel('Jarak (cm)')
        self.ax.set_ylabel('Amplituda')
        self.ax.set_title('Hasil Deteksi Kandungan Air Tanah')
        self.ax.grid(True)
        self.canvas.draw()

def load_setting(self) -> dict:
    logging.debug("Memuat setting dari file JSON")
    
    file_path = "./swam/setting_data.json"
    try:
        with open(file_path, 'r') as file:
            settings = json.loads(file.read())
            logging.debug(f"Setting berhasil dimuat: {settings}")
            return settings
    except FileNotFoundError:
        logging.error(f"File setting tidak ditemukan: {file_path}")
        return {}