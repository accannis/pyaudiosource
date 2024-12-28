"""
Audio level metering functionality
"""

import numpy as np
from typing import Tuple, Optional

class AudioMeter:
    """
    Provides audio level metering with peak and RMS measurements
    
    Args:
        window_size (int): Size of the window for RMS calculation in samples (default: 1024)
        peak_hold_time (float): Time to hold peak value in seconds (default: 1.0)
        sample_rate (int): Sample rate in Hz (default: 44100)
    """
    
    def __init__(
        self,
        window_size: int = 1024,
        peak_hold_time: float = 1.0,
        sample_rate: int = 44100
    ):
        self.window_size = window_size
        self.peak_hold_time = peak_hold_time
        self.sample_rate = sample_rate
        
        self.peak_hold_samples = int(peak_hold_time * sample_rate)
        self.current_peak = 0.0
        self.peak_hold_counter = 0
        self.last_rms = 0.0
    
    def process(self, audio_data: np.ndarray) -> Tuple[float, float]:
        """
        Process audio data and return current levels
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Tuple of (RMS level, Peak level)
        """
        # Calculate RMS
        if len(audio_data) > 0:
            self.last_rms = np.sqrt(np.mean(np.square(audio_data)))
        
        # Calculate peak
        if len(audio_data) > 0:
            current_peak = np.max(np.abs(audio_data))
            if current_peak > self.current_peak:
                self.current_peak = current_peak
                self.peak_hold_counter = self.peak_hold_samples
            elif self.peak_hold_counter > 0:
                self.peak_hold_counter -= len(audio_data)
            else:
                self.current_peak = current_peak
        
        return self.last_rms, self.current_peak
    
    def get_levels_db(self) -> Tuple[float, float]:
        """
        Get current levels in decibels
        
        Returns:
            Tuple of (RMS level in dB, Peak level in dB)
        """
        rms_db = 20 * np.log10(max(self.last_rms, 1e-10))
        peak_db = 20 * np.log10(max(self.current_peak, 1e-10))
        return rms_db, peak_db
