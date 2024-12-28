"""
Example script to test the audio GUI functionality
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication
from pyaudiosource import AudioTestWindow

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudioTestWindow()
    window.show()
    sys.exit(app.exec())
