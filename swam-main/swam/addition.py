from enum import Enum
import typing

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QMessageBox, QWidget, QDialog, QTextEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt



class PopUpLevel(Enum):
    INFO = 1
    WARN = 2
    CRITICAL = 3


def get_popup(message: str, level: PopUpLevel, parent: typing.Optional[QWidget] = None):

    if level == PopUpLevel.INFO:
        QMessageBox.information(parent, "Information", message)
    elif level.WARN == PopUpLevel.WARN:
        QMessageBox.warning(parent, "Warning", message)
    elif level.CRITICAL == PopUpLevel.CRITICAL:
        QMessageBox.critical(parent, "Critical", message)



class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        # Add title
        title = QLabel('Selamat Datang di Aplikasi SWAM-Radar!')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-family: Georgia; font-size: 36px; font-weight: bold;")

        # Add subtitle
        subtitle = QLabel('Aplikasi ini merupakan alat untuk analisis hasil deteksi dan pemetaan KAT \n secara otomatis dan real-time menggunakan sistem radar SFCW')
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-family: Georgia; font-size: 24px;")

        # Create a grid layout for the images
        grid_layout = QGridLayout()
        image_size = (550, 450)  # Width, Height

        # Load and add images
        pixmap1 = QPixmap("./swam/assets/2.png").scaled(*image_size, Qt.KeepAspectRatio)
        label1 = QLabel()
        label1.setPixmap(pixmap1)
        label1.setAlignment(Qt.AlignCenter)
        grid_layout.addWidget(label1, 0, 1, Qt.AlignCenter)

        caption1 = QLabel('Fitur Grafik Deteksi KAT')
        caption1.setAlignment(Qt.AlignCenter)
        caption1.setStyleSheet("font-family: Georgia; font-size: 18px;")
        grid_layout.addWidget(caption1, 1, 1, Qt.AlignCenter)

        pixmap2 = QPixmap("./swam/assets/1.png").scaled(*image_size, Qt.KeepAspectRatio)
        label2 = QLabel()
        label2.setPixmap(pixmap2)
        label2.setAlignment(Qt.AlignCenter)
        grid_layout.addWidget(label2, 0, 0, Qt.AlignCenter)

        caption2 = QLabel('Fitur Pemetaan KAT')
        caption2.setAlignment(Qt.AlignCenter)
        caption2.setStyleSheet("font-family: Georgia; font-size: 18px;")
        grid_layout.addWidget(caption2, 1, 0, Qt.AlignCenter)

        # Add grid layout to the main layout
        main_layout.addStretch(1)
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addStretch(1)
        main_layout.addLayout(grid_layout)
        main_layout.addStretch(1)

        # Set the main layout for the window
        self.setLayout(main_layout)


class HelpWindow(QDialog):
    def __init__(self, parent=None) -> None:
        super(HelpWindow, self).__init__(parent)

        self.setWindowTitle("Bantuan?")
        # self.setMinimumSize(550,230)
        self.setFixedSize(500,500)
        

        # Membuat label-label untuk setiap langkah prosedur
        judulnya = QLabel("Prosedur penggunaan aplikasi:")
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(
            "Aplikasi SWAM merupakan software Graphical User Interface (GUI) yang dapat menampilkan visualisasi hasil deteksi radar dalam bentuk grafik pemetaan KAT"
            "\n\n=============================================\n"
            "1. Mengatur port sesuai dengan perangkat keras yang tersambung\n"
            "2. Pilih menu utama, yaitu 'Grafik KAT' untuk hasil grafik dan      'Pemetaan KAT' untuk hasil pemetaan KAT\n"
            "3. Isi formulir nama petugas, lokasi dan tanggal pengambilan data\n"
            "4. Klik 'Start Scan' untuk memulai deteksi radar dan menjalankan GPS\n"
            "5. Klik 'Stop Scan' untuk berhenti mendeteksi radar dan berhenti menjalankan GPS\n"
            "6. Klik 'Save Data' untuk menyimpan data hasil deteksi radar dan koordinat GPS\n"
            "7. Klik 'Reset Data' untuk mengosongkan data dan membersihkan    hasil plot, sebelum memulai deteksi kembali"
            "\n=============================================\n\n"
            "Hasil data yang disimpan dari menu 'Grafik KAT' adalah data deteksi radar dalam bentuk real+imajiner dan data yang telah diproses, yaitu sinyal terima\n\n"
            "Hasil data yang disimpan dari menu 'Pemetaan KAT' adalah data koordinat GPS dan data deteksi radar yang telah diproses, yaitu nilai estimasi KAT"

        )


        font = judulnya.font()
        font.setPointSize(14)
        font.setBold(True)
        font.setFamily("Georgia")
        subfont = text_edit.font()
        subfont.setPointSize(11)
        subfont.setFamily("Georgia")
        judulnya.setFont(font)
        text_edit.setFont(subfont)

        layout = QVBoxLayout()
        layout.addWidget(judulnya)
        layout.addWidget(text_edit)

        # layout.addWidget(QLabel("cc: Muhammad Surya Sanjiwani"))

        self.setLayout(layout)
    