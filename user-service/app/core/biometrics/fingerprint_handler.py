import os
import ctypes
from ctypes import wintypes
import time
from typing import Optional, Tuple
import win32api
import win32con
import win32security
import win32file
import pywintypes

class FingerPrintHandler:
    def __init__(self):
        self.dll_path = os.path.join(os.path.dirname(__file__), 'dpFPReg.dll')
        self.dll = None
        self.device_handle = None
        self.initialized = False

    def initialize(self) -> bool:
        """Initialize fingerprint device"""
        try:
            # Load DLL
            self.dll = ctypes.WinDLL(self.dll_path)
            
            # Define function prototypes
            self.dll.OpenDevice.argtypes = [ctypes.POINTER(wintypes.HANDLE)]
            self.dll.OpenDevice.restype = wintypes.BOOL
            
            self.dll.CloseDevice.argtypes = [wintypes.HANDLE]
            self.dll.CloseDevice.restype = wintypes.BOOL
            
            self.dll.CaptureFingerprint.argtypes = [
                wintypes.HANDLE,
                ctypes.POINTER(ctypes.c_ubyte),
                ctypes.POINTER(ctypes.c_int)
            ]
            self.dll.CaptureFingerprint.restype = wintypes.BOOL

            # Open device
            device_handle = wintypes.HANDLE()
            if not self.dll.OpenDevice(ctypes.byref(device_handle)):
                raise Exception("Failed to open fingerprint device")
            
            self.device_handle = device_handle
            self.initialized = True
            return True

        except Exception as e:
            print(f"Initialization error: {str(e)}")
            self.initialized = False
            return False

    def capture_fingerprint(self) -> Optional[bytes]:
        """Capture fingerprint and return template"""
        if not self.initialized or not self.device_handle:
            raise Exception("Device not initialized")

        try:
            # Allocate buffer for fingerprint template
            template_size = ctypes.c_int(0)
            max_template_size = 2048
            template_buffer = (ctypes.c_ubyte * max_template_size)()

            # Capture fingerprint
            if not self.dll.CaptureFingerprint(
                self.device_handle,
                template_buffer,
                ctypes.byref(template_size)
            ):
                raise Exception("Failed to capture fingerprint")

            # Convert captured data to bytes
            template_data = bytes(template_buffer[:template_size.value])
            return template_data

        except Exception as e:
            print(f"Capture error: {str(e)}")
            return None

    def verify_fingerprint(self, stored_template: bytes, current_template: bytes) -> bool:
        """Verify if two fingerprint templates match"""
        if not self.initialized:
            raise Exception("Device not initialized")

        try:
            # Define verification function
            self.dll.VerifyFingerprint.argtypes = [
                ctypes.c_char_p,
                ctypes.c_int,
                ctypes.c_char_p,
                ctypes.c_int
            ]
            self.dll.VerifyFingerprint.restype = wintypes.BOOL

            # Perform verification
            result = self.dll.VerifyFingerprint(
                stored_template,
                len(stored_template),
                current_template,
                len(current_template)
            )
            return bool(result)

        except Exception as e:
            print(f"Verification error: {str(e)}")
            return False

    def close(self):
        """Close the fingerprint device"""
        try:
            if self.device_handle:
                self.dll.CloseDevice(self.device_handle)
                self.device_handle = None
            self.initialized = False
        except Exception as e:
            print(f"Close error: {str(e)}") 