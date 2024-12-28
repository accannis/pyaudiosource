"""
GUI test script for pyaudiosource package
"""

import sys
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QComboBox, QProgressBar, QLabel, QSlider
)
from PyQt6.QtCore import Qt, QTimer
from pyaudiosource import AudioSource, AudioMeter, DeviceManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AudioTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyAudioSource Test")
        self.setMinimumWidth(400)
        
        # Create central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create device selector
        self.device_selector = QComboBox()
        self.device_selector.currentIndexChanged.connect(self.on_device_changed)
        layout.addWidget(QLabel("Input Device:"))
        layout.addWidget(self.device_selector)
        
        # Create gain slider
        self.gain_slider = QSlider(Qt.Orientation.Horizontal)
        self.gain_slider.setMinimum(0)
        self.gain_slider.setMaximum(200)
        self.gain_slider.setValue(100)
        self.gain_slider.valueChanged.connect(self.on_gain_changed)
        layout.addWidget(QLabel("Input Gain:"))
        layout.addWidget(self.gain_slider)
        
        # Create level meters
        self.rms_meter = QProgressBar()
        self.peak_meter = QProgressBar()
        self.rms_meter.setMinimum(-60)
        self.rms_meter.setMaximum(0)
        self.peak_meter.setMinimum(-60)
        self.peak_meter.setMaximum(0)
        
        layout.addWidget(QLabel("RMS Level:"))
        layout.addWidget(self.rms_meter)
        layout.addWidget(QLabel("Peak Level:"))
        layout.addWidget(self.peak_meter)
        
        # Add numeric level display
        self.level_label = QLabel("Levels: ---")
        layout.addWidget(self.level_label)
        
        # Set up audio components
        self.audio_source = AudioSource(sample_rate=44100, channels=1)
        self.meter = AudioMeter(peak_hold_time=1.0)
        self.audio_source.set_callback(self.audio_callback)
        
        # Populate device list
        self.populate_devices()
        
        # Start update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(50)  # 50ms = 20 fps
        
        # Show window
        self.show()
        self.raise_()
    
    def populate_devices(self):
        """Populate the device selector"""
        self.device_selector.clear()
        self.devices = DeviceManager.list_devices()
        for idx, name in self.devices:
            self.device_selector.addItem(name, idx)
        
        # Select default device
        default_device = DeviceManager.get_default_device()
        if default_device is not None:
            for i, (idx, _) in enumerate(self.devices):
                if idx == default_device:
                    self.device_selector.setCurrentIndex(i)
                    break
    
    def on_device_changed(self, index):
        """Handle device selection"""
        if index >= 0:
            device_index = self.device_selector.currentData()
            self.audio_source.start(device_index)
    
    def on_gain_changed(self, value):
        """Handle gain slider changes"""
        gain = value / 100.0
        self.audio_source.set_gain(gain)
    
    def audio_callback(self, data, level):
        """Handle audio data"""
        self.meter.process(data)
    
    def update_display(self):
        """Update the GUI display"""
        rms_db, peak_db = self.meter.get_levels_db()
        
        # Update progress bars
        self.rms_meter.setValue(int(max(-60, min(0, rms_db))))
        self.peak_meter.setValue(int(max(-60, min(0, peak_db))))
        
        # Update numeric display
        self.level_label.setText(f"RMS: {rms_db:6.1f} dB  Peak: {peak_db:6.1f} dB")
    
    def closeEvent(self, event):
        """Handle window close"""
        self.audio_source.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudioTestWindow()
    sys.exit(app.exec())
