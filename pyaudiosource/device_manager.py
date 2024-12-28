"""
Audio device management functionality
"""

import logging
import sounddevice as sd
from typing import List, Tuple, Dict, Optional

class DeviceManager:
    """
    Manages audio input devices and their selection
    """
    
    @staticmethod
    def list_devices() -> List[Tuple[int, str]]:
        """
        List all available input devices
        
        Returns:
            List of tuples containing (device index, device name)
        """
        devices = []
        try:
            for i, dev in enumerate(sd.query_devices()):
                if dev['max_input_channels'] > 0:
                    device_name = f"{dev['name']}"
                    devices.append((i, device_name))
                    logging.info(f"Found input device {i}: {device_name}")
        except Exception as e:
            logging.error(f"Error listing audio devices: {e}", exc_info=True)
        return devices
    
    @staticmethod
    def get_default_device() -> Optional[int]:
        """
        Get the default input device index
        
        Returns:
            Device index or None if no devices found
        """
        try:
            devices = DeviceManager.list_devices()
            if not devices:
                return None
            
            # Try to find MacBook Pro microphone first
            for idx, name in devices:
                if "MacBook Pro Microphone" in name:
                    logging.info(f"Found MacBook Pro Microphone: {idx}")
                    return idx
            
            # Fall back to system default
            default_idx = sd.default.device[0]
            logging.info(f"Using system default device: {default_idx}")
            return default_idx
            
        except Exception as e:
            logging.error(f"Error getting default device: {e}", exc_info=True)
            return None
    
    @staticmethod
    def get_device_info(device_index: int) -> Optional[Dict]:
        """
        Get detailed information about a device
        
        Args:
            device_index: Index of the device
            
        Returns:
            Dictionary containing device information or None if device not found
        """
        try:
            return sd.query_devices(device_index)
        except Exception as e:
            logging.error(f"Error getting device info: {e}", exc_info=True)
            return None
