import typing
import json
import os
import logging

from PyQt5.QtWidgets import QDialog, QLabel, QWidget, QPushButton, QLineEdit, QTextEdit, QFormLayout
from serial.tools.list_ports import comports
from swam.addition import PopUpLevel, get_popup

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SettingWindow(QDialog):
    def __init__(self, parent: typing.Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Pengaturan Port")
        self.setMinimumSize(280, 320)
        
        logging.info("Initializing SettingWindow")
        
        device_port = self._load_setting()

        self.radar_port_read = str(device_port.get("radar_port"))
        self.gps_port_read = str(device_port.get("gps_port"))

        refresh_btn = QPushButton("Periksa Daftar Port")
        save_btn = QPushButton("Simpan Pengaturan")
        refresh_btn.clicked.connect(self._refresh_port) 
        save_btn.clicked.connect(self._save_port)

        self.radar_port = QLineEdit(self.radar_port_read)
        self.gps_port = QLineEdit(self.gps_port_read)
        self.port_list = QTextEdit()
        self.port_list.setReadOnly(True)

        self.label_vna_port = QLabel("VNA Port")
        self.label_gps_port = QLabel("GPS Port")
        self.label_port_list = QLabel("Daftar Port")

        self.setting_layout = QFormLayout()
        self.setting_layout.addRow(self.label_vna_port, self.radar_port)
        self.setting_layout.addRow(self.label_gps_port, self.gps_port)
        self.setting_layout.addRow(self.label_port_list, self.port_list)
        self.setting_layout.addRow(save_btn)
        self.setting_layout.addRow(refresh_btn)

        font = self.font()
        font.setPointSize(10)
        self.radar_port.setFont(font)
        self.gps_port.setFont(font)
        self.port_list.setFont(font)
        font.setPointSize(11)
        self.label_vna_port.setFont(font)
        self.label_gps_port.setFont(font)
        self.label_port_list.setFont(font)
        save_btn.setFont(font)
        refresh_btn.setFont(font)

        self._refresh_port()
        self.setLayout(self.setting_layout)

    def _save_port(self):
        setting_data = {
            "radar_port": self.radar_port.text(),
            "gps_port": self.gps_port.text()
        }
        logging.debug(f"Saving settings: {setting_data}")

        json_file_path = "./swam/setting_data.json"

        try:
            with open(json_file_path, 'w') as jsfile:
                json.dump(setting_data, jsfile)
            logging.info("Settings saved successfully")
            get_popup("Pengaturan disimpan!", PopUpLevel.INFO, self)
        except Exception as e:
            logging.error(f"Failed to save settings: {e}")

    def _refresh_port(self):
        logging.debug("Refreshing port list")
        ports = comports()
        self.port_list.clear()

        if len(ports) < 1:
            self.port_list.setText("Tidak ada perangkat terhubung!")
            logging.info("No devices connected")
            return

        i = 1  # Variable for numbering
        for port in ports:
            port_info = f"{i}. Perangkat Terdeteksi: {port.device}"  # Add numbering
            self.port_list.append(port_info)
            i += 1  # Increment i for next iteration
        logging.info("Port list refreshed successfully")

    def _load_setting(self) -> dict:
        file_path = "./swam/setting_data.json"
        try:
            with open(file_path, 'r') as file:
                settings = json.loads(file.read())
                logging.debug(f"Loaded settings: {settings}")
                return settings
        except FileNotFoundError:
            logging.warning("Settings file not found, returning empty settings")
            return {}
