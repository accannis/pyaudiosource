# PyAudioSource

A Python package for audio input handling and metering. This package provides a simple interface for:
- Audio input device selection and management
- Real-time audio level metering (RMS and peak)
- Gain control
- Audio buffer management

## Installation

```bash
pip install pyaudiosource
```

## Quick Start

```python
from pyaudiosource import AudioSource, AudioMeter, DeviceManager

# List available input devices
devices = DeviceManager.list_devices()
for idx, name in devices:
    print(f"Device {idx}: {name}")

# Create an audio source with default settings
audio_source = AudioSource(sample_rate=44100, channels=1)

# Create an audio meter
meter = AudioMeter()

# Define a callback to process audio data
def audio_callback(data, level):
    rms, peak = meter.process(data)
    print(f"RMS: {rms:.2f} dB, Peak: {peak:.2f} dB")

# Set the callback
audio_source.set_callback(audio_callback)

# Start audio input using the default device
default_device = DeviceManager.get_default_device()
if default_device is not None:
    audio_source.start(default_device)
```

## Features

### Audio Source
- Configurable sample rate, channels, and buffer sizes
- Gain control
- Callback-based audio processing
- Thread-safe audio buffer management

### Audio Meter
- RMS level measurement
- Peak level with configurable hold time
- dB conversion

### Device Manager
- List available input devices
- Get default device
- Get detailed device information

## Requirements

- Python 3.8+
- numpy
- sounddevice

## License

MIT License
