"""
Core audio input handling functionality
"""

import queue
import threading
import logging
import numpy as np
import sounddevice as sd
from typing import Callable, Optional, Union, Dict, Any

AudioCallback = Callable[[np.ndarray, float], None]

class AudioSource:
    """
    Handles audio input from a selected device with gain control and level metering.
    
    Args:
        sample_rate (int): Sample rate in Hz (default: 44100)
        channels (int): Number of input channels (default: 1)
        frame_size (int): Size of each audio frame in samples (default: 1024)
        buffer_size (int): Size of the internal buffer in samples (default: 44100)
        device_index (Optional[int]): Index of input device to use (default: None, uses system default)
        gain (float): Input gain multiplier (default: 1.0)
    """
    
    def __init__(
        self,
        sample_rate: int = 44100,
        channels: int = 1,
        frame_size: int = 1024,
        buffer_size: int = 44100,
        device_index: Optional[int] = None,
        gain: float = 1.0
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.frame_size = frame_size
        self.buffer_size = buffer_size
        self.gain = gain
        
        # Initialize audio buffer and state
        self.audio_buffer = np.zeros(buffer_size, dtype=np.float32)
        self.should_stop = False
        self.stream = None
        self.current_device = device_index
        
        # Queue for audio data
        self.audio_queue = queue.Queue()
        
        # Callback for client code
        self.callback: Optional[AudioCallback] = None
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._audio_processor)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        # Start audio stream if device specified
        if device_index is not None:
            self.start(device_index)
    
    def start(self, device_index: int) -> None:
        """Start audio input from specified device"""
        try:
            logging.info(f"Starting audio stream with device {device_index}")
            if self.stream is not None:
                logging.info("Stopping existing stream...")
                self.stream.stop()
                self.stream.close()
            
            # Get device info
            device_info = sd.query_devices(device_index, 'input')
            logging.info(f"Device info: {device_info}")
            
            # Configure stream parameters
            self.current_device = device_index
            logging.info(f"Opening stream with sample rate {self.sample_rate}Hz, channels: {self.channels}")
            
            # Create and start stream
            self.stream = sd.InputStream(
                device=device_index,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.frame_size,
                callback=self._audio_callback,
                dtype=np.float32
            )
            logging.info("Stream created, starting...")
            self.stream.start()
            logging.info("Audio stream started successfully")
            
        except Exception as e:
            logging.error(f"Error starting audio stream: {e}", exc_info=True)
            raise
    
    def stop(self) -> None:
        """Stop audio input"""
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
    
    def set_gain(self, gain: float) -> None:
        """Set input gain"""
        self.gain = max(0.0, gain)
    
    def set_callback(self, callback: AudioCallback) -> None:
        """Set callback for audio data"""
        self.callback = callback
    
    def get_buffer(self) -> np.ndarray:
        """Get current audio buffer"""
        return self.audio_buffer.copy()
    
    def _audio_callback(self, indata: np.ndarray, frames: int, time: Any, status: Any) -> None:
        """Internal callback for audio data"""
        try:
            if status:
                logging.warning(f"Audio callback status: {status}")
            
            # Get the raw audio level
            raw_level = np.abs(indata).mean()
            if raw_level > 0.0001:  # Only log when there's significant audio
                logging.debug(f"Raw audio level: {raw_level:.6f}")
            
            # Apply gain
            indata = indata * self.gain
            
            # Put the data in the queue
            self.audio_queue.put_nowait((indata.copy(), raw_level * self.gain))
            
        except Exception as e:
            logging.error(f"Error in audio callback: {e}", exc_info=True)
    
    def _audio_processor(self) -> None:
        """Process audio data from queue"""
        logging.info("Starting audio processor thread")
        while not self.should_stop:
            try:
                # Get data from queue with timeout
                indata, level = self.audio_queue.get(timeout=0.1)
                
                # Roll the buffer and add new data
                samples_to_add = len(indata)
                self.audio_buffer = np.roll(self.audio_buffer, -samples_to_add)
                self.audio_buffer[-samples_to_add:] = indata.flatten()
                
                # Call client callback if set
                if self.callback:
                    self.callback(indata, level)
                    
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error processing audio: {e}", exc_info=True)
                continue
    
    def __del__(self):
        """Cleanup resources"""
        self.should_stop = True
        self.stop()
