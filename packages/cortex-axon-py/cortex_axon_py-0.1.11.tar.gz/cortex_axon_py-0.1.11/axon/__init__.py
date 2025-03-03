from .header_capture import capture_inbound_headers
from .session import patch_requests

def setup_auto_header_forwarding(patch: bool = True):
    """
    Optionally monkey-patches requests to auto-inject headers stored in a context variable.
    
    In your inbound request handler, call `capture_inbound_headers(headers)`
    with the incoming request's headers.
    """
    if patch:
        patch_requests()
