"""
PyAudioSource - A Python package for audio input handling and metering
"""

from .audio_source import AudioSource, AudioCallback
from .audio_meter import AudioMeter
from .device_manager import DeviceManager

__version__ = "0.1.0"
__all__ = ['AudioSource', 'AudioCallback', 'AudioMeter', 'DeviceManager']
