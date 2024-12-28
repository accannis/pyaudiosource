"""
Simple test script for pyaudiosource package
"""

import sys
import time
import logging
from pyaudiosource import AudioSource, AudioMeter, DeviceManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def audio_callback(data, level):
    """Called for each chunk of audio data"""
    # Calculate audio levels
    rms, peak = meter.process(data)
    rms_db, peak_db = meter.get_levels_db()
    
    # Create a visual meter
    meter_width = 50
    meter_chars = int(max(0, min(meter_width, (level * meter_width))))
    meter_display = '#' * meter_chars + '-' * (meter_width - meter_chars)
    
    # Print levels
    print(f"\rLevel: [{meter_display}] RMS: {rms_db:6.1f}dB Peak: {peak_db:6.1f}dB", end='')

if __name__ == '__main__':
    try:
        # List available devices
        print("Available input devices:")
        devices = DeviceManager.list_devices()
        for idx, name in devices:
            print(f"{idx}: {name}")
        
        # Get default device
        device_index = DeviceManager.get_default_device()
        if device_index is None:
            print("No input devices found!")
            sys.exit(1)
        
        # Create audio components
        audio_source = AudioSource(sample_rate=44100, channels=1)
        meter = AudioMeter(peak_hold_time=1.0)
        
        # Set up callback
        audio_source.set_callback(audio_callback)
        
        # Start audio input
        print(f"\nStarting audio input from device {device_index}...")
        audio_source.start(device_index)
        
        print("\nRecording... Press Ctrl+C to stop")
        
        # Keep running until interrupted
        while True:
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        if 'audio_source' in locals():
            audio_source.stop()
        print("Done.")
