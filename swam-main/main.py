from PyQt5.QtWidgets import QApplication
import sys
import qdarktheme
from swam.gui import MainWindow
import logging

# def main():
    
#     app = QApplication([])

#     ex = MainWindow()
#     ex.show()

#     app.setStyleSheet(qdarktheme.load_stylesheet("light"))
#     sys.exit(app.exec())



# if __name__ == '__main__': 
#     main()

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)


def main():
    logging.info("Application is starting")
    
    try:
        app = QApplication([])

        logging.debug("Creating main window instance")
        ex = MainWindow()
        ex.show()

        logging.debug("Setting application stylesheet")
        app.setStyleSheet(qdarktheme.load_stylesheet("light"))
        
        logging.info("Entering main event loop")
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()