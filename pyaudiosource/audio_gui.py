"""
GUI components for pyaudiosource package
"""

import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QComboBox, QProgressBar, QLabel, QSlider
)
from PyQt6.QtCore import Qt, QTimer
from .audio_source import AudioSource
from .audio_meter import AudioMeter
from .device_manager import DeviceManager

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
        
        layout.addWidget(QLabel("RMS Level (dB):"))
        layout.addWidget(self.rms_meter)
        layout.addWidget(QLabel("Peak Level (dB):"))
        layout.addWidget(self.peak_meter)
        
        # Initialize audio components
        self.device_manager = DeviceManager()
        self.audio_source = AudioSource()
        self.audio_meter = AudioMeter()
        
        # Set up audio callback
        self.audio_source.set_callback(self.process_audio)
        
        # Update device list
        self.update_device_list()
        
        # Start audio
        self.start_audio()
        
        # Update timer for UI
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_meters)
        self.update_timer.start(50)  # 50ms refresh rate
        
    def update_device_list(self):
        """Update the device selector with available input devices"""
        self.device_selector.clear()
        devices = self.device_manager.list_devices()
        for idx, name in devices:
            self.device_selector.addItem(name, idx)
            
    def start_audio(self):
        """Start audio input"""
        device_idx = self.device_selector.currentData()
        if device_idx is not None:
            self.audio_source.start(device_idx)
            
    def stop_audio(self):
        """Stop audio input"""
        self.audio_source.stop()
        
    def process_audio(self, indata, level, *args):
        """Process audio data"""
        self.audio_meter.process(indata)
        
    def update_meters(self):
        """Update the level meters"""
        rms_db = self.audio_meter.get_rms_db()
        peak_db = self.audio_meter.get_peak_db()
        
        # Update progress bars
        self.rms_meter.setValue(int(rms_db))
        self.peak_meter.setValue(int(peak_db))
        
        # Update color based on level
        self.update_meter_color(self.rms_meter, rms_db)
        self.update_meter_color(self.peak_meter, peak_db)
        
    def update_meter_color(self, meter, level):
        """Update meter color based on level"""
        if level > -3:
            color = "red"
        elif level > -12:
            color = "yellow"
        else:
            color = "#2ecc71"  # Green
            
        meter.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
        
    def on_device_changed(self, index):
        """Handle device selection change"""
        self.stop_audio()
        self.start_audio()
        
    def on_gain_changed(self, value):
        """Handle gain slider change"""
        gain = value / 100.0
        self.audio_source.set_gain(gain)
        
    def closeEvent(self, event):
        """Clean up when window is closed"""
        self.stop_audio()
        super().closeEvent(event)
