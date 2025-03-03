from .header_capture import capture_inbound_headers
from .session import patch_requests

def setup_auto_header_forwarding(patch: bool = True):
    """
    if patch:
        patch_requests()
