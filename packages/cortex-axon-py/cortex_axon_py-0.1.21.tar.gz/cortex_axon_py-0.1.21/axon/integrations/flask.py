from axon.session import capture_inbound_headers, patch_requests

def setup_flask_auto_header_forwarding(app):
    """
    Call this with your Flask app instance.
    It registers a before_request hook to capture inbound headers.
    """
    @app.before_request
    def _capture_headers():
        from flask import request
        capture_inbound_headers(request.headers)
    
    patch_requests()
