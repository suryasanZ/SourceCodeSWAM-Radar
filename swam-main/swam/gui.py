import logging
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QGridLayout, QFormLayout, QDateEdit, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QTabWidget, QPushButton
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon, QFont, QPixmap
from .addition import Dashboard
from .addition import HelpWindow
from .content import DataGraph
from .content import DataMap
from swam.settings import SettingWindow

# Configure logging to show debug messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class MainWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        logging.info("Inisialisasi MainWindow")

        self.setWindowIcon(QIcon("./swam/assets/logo.png"))
        self.setWindowTitle("SWAM APP")
        self.setMinimumSize(1024, 768)

        self.setting_dialog = SettingWindow(self)
        self.help_dialog = HelpWindow(self)

        self.button_style= """
            QPushButton { 
                background: #015693;
                border-radius: .5em;
                border: 2px solid #FFF;
                color: #FFF;
                width: 15px;
                height: 25px;
                font: 12pt Arial;
                font-weight: bold;
                padding: 5px;
            }

            QPushButton:hover {
                background: #025159;
            }
            """
        self.window_button_style= """
            QPushButton { 
                background: #677E92;
                border-radius: .5em;
                border: 2px solid #FFF;
                color: #FFF;
                width: 15px;
                height: 25px;
                font: 12pt Arial;
                font-weight: bold;
                padding: 5px;
            }

            QPushButton:hover {
                background: #025159;
            }
            """

        self.btn_dashboard = QPushButton("Dashboard", self)
        self.btn_dashboard.setStyleSheet(self.button_style)

        self.btn_datagraph = QPushButton("Grafik KAT", self)
        self.btn_datagraph.setStyleSheet(self.button_style)

        self.btn_datamapplot = QPushButton("Pemetaan KAT", self)
        self.btn_datamapplot.setStyleSheet(self.button_style)

        self.btn_setting = QPushButton("Pengaturan", self) 
        self.btn_setting.setStyleSheet(self.window_button_style)

        self.btn_help = QPushButton("Bantuan ?", self)  
        self.btn_help.setStyleSheet(self.window_button_style)

        self.btn_dashboard.clicked.connect(self.button1)
        self.btn_datagraph.clicked.connect(self.button2)
        self.btn_datamapplot.clicked.connect(self.button3)
        self.btn_setting.clicked.connect(self.button4)
        self.btn_help.clicked.connect(self.button5)

        self.date_format = "dd/MM/yyyy"
        self.date_input = QDateEdit(calendarPopup=True)
        self.date_input.setDisplayFormat(self.date_format)
        self.date_input.setDateTime(QDateTime.currentDateTime())

        font_style = QFont()
        font_style.setPointSize(11)  
        font_style.setFamily("Arial")

        lbl_name = QLabel("Nama:")
        lbl_name.setFont(font_style)
        lbl_loc = QLabel("Tempat:")
        lbl_loc.setFont(font_style)
        lbl_date = QLabel("Tanggal:")
        lbl_date.setFont(font_style)
        lbl_number = QLabel("Data Point:")
        lbl_number.setFont(font_style)

        self.txt_name = QLineEdit()
        self.txt_loc = QLineEdit()
        self.txt_number = QLineEdit()

        # Creating a form layout and adding widgets
        self.form_layout = QFormLayout()
        self.form_layout.addRow(lbl_name, self.txt_name)
        self.form_layout.addRow(lbl_loc, self.txt_loc)
        self.form_layout.addRow(lbl_date, self.date_input)

        title_label = QLabel("SWAM-Radar")
        title_font = QFont("Georgia")
        title_font.setBold(True)
        title_font.setPointSize(18)  # Set the font size to 14 (adjust as needed)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)  # Align text to center

        subtitle_label = QLabel("Soil Water Analysis \nand Mapping using Radar")
        subtitle_font = QFont("Georgia")
        subtitle_font.setPointSize(12)  # Set the font size to 14 (adjust as needed)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)

        image_size = (50, 100)
        logo_telyu = QPixmap("./swam/assets/Logo_telyu2.png").scaled(*image_size, Qt.KeepAspectRatio)
        logo1 = QLabel()
        logo1.setPixmap(logo_telyu)
        logo1.setAlignment(Qt.AlignRight)
        
        logo_isiot = QPixmap("./swam/assets/Logo_IS-IOT2.png").scaled(*image_size, Qt.KeepAspectRatio)
        logo2 = QLabel()
        logo2.setPixmap(logo_isiot)
        logo2.setAlignment(Qt.AlignLeft)

        logo_layout = QGridLayout()
        logo_layout.addWidget(logo1, 0, 0, Qt.AlignRight)
        logo_layout.addWidget(logo2, 0, 1, Qt.AlignLeft)

        left_layout = QVBoxLayout()
        left_layout.addWidget(title_label)
        left_layout.addWidget(subtitle_label)
        left_layout.addLayout(logo_layout)
        left_layout.addWidget(self.btn_datamapplot)
        left_layout.addWidget(self.btn_datagraph)
        left_layout.addStretch(1)
        left_layout.addStretch(5)
        left_layout.addWidget(self.btn_setting)
        left_layout.addWidget(self.btn_help)
        left_layout.setSpacing(20)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        # add tabs
        self.tab1 = Dashboard()
        self.tab2 = DataGraph()
        self.tab3 = DataMap()

        self.right_widget = QTabWidget()
        self.right_widget.tabBar().setObjectName("mainTab")

        self.right_widget.addTab(self.tab1, '')
        self.right_widget.addTab(self.tab2, '')
        self.right_widget.addTab(self.tab3, '')

        self.right_widget.setCurrentIndex(0)
        self.right_widget.setStyleSheet('''QTabBar::tab{width: 0; \
            height: 0; margin: 0; padding: 0; border: none;}''')

        main_layout = QHBoxLayout()
        main_layout.addWidget(left_widget)
        main_layout.addWidget(self.right_widget)
        main_layout.setStretch(0, 40)
        main_layout.setStretch(1, 200)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        logging.info("MainWindow initialized successfully")

    def button1(self):
        logging.debug("Dashboard button clicked")
        self.right_widget.setCurrentIndex(0)

    def button2(self):
        logging.debug("Grafik KAT button clicked")
        self.right_widget.setCurrentIndex(1)

    def button3(self):
        logging.debug("Pemetaan KAT button clicked")
        self.right_widget.setCurrentIndex(2)

    def button4(self):
        logging.debug("Pengaturan button clicked")
        self.setting_dialog.exec()

    def button5(self):
        logging.debug("Bantuan button clicked")
        self.help_dialog.exec()

# Test logging
logging.debug("Debugging mode enabled")
logging.info("Info level logging test")
logging.warning("Warning level logging test")
