import winbio
from typing import Optional

class WBFHandler:
    def __init__(self):
        self.unit_id = None
        self.session_handle = None

    async def initialize(self):
        """Initialize WBF session"""
        try:
            self.session_handle = winbio.OpenSession(
                winbio.BioAPIVersion(1, 0),
                winbio.DATABASE_DEFAULT,
                winbio.POOL_TYPE_SYSTEM,
                None,
                0,
                None,
                0
            )
            return True
        except Exception as e:
            print(f"Failed to initialize WBF: {e}")
            return False

    async def capture_fingerprint(self) -> Optional[str]:
        """Capture fingerprint using WBF"""
        try:
            template = winbio.CaptureSample(
                self.session_handle,
                winbio.PURPOSE_VERIFY,
                0,
                self.unit_id,
                None
            )
            return template.encode('base64').decode()
        except Exception as e:
            print(f"Failed to capture fingerprint: {e}")
            return None

    async def close(self):
        """Close WBF session"""
        if self.session_handle:
            winbio.CloseSession(self.session_handle) 