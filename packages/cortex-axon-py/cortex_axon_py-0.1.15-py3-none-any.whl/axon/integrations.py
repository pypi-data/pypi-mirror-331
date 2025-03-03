from axon.session import capture_inbound_headers, patch_requests

# ---------- Flask Integration ----------

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

# ---------- Django Integration ----------

class DjangoCaptureHeadersMiddleware:
    """
    Django middleware that captures inbound headers.
    Just add this class to your MIDDLEWARE list.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        headers = {}
        for key, value in request.META.items():
            if key.startswith("HTTP_"):
                header_name = key[5:].replace("_", "-").title()
                headers[header_name] = value
        if "CONTENT_TYPE" in request.META:
            headers["Content-Type"] = request.META["CONTENT_TYPE"]
        if "CONTENT_LENGTH" in request.META:
            headers["Content-Length"] = request.META["CONTENT_LENGTH"]

        capture_inbound_headers(headers)
        return self.get_response(request)

# ---------- FastAPI Integration ----------

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class FastAPICaptureHeadersMiddleware(BaseHTTPMiddleware):
    """
    FastAPI/Starlette middleware to capture inbound headers.
    Add this middleware to your FastAPI app.
    """
    async def dispatch(self, request: Request, call_next):
        capture_inbound_headers(dict(request.headers))
        response = await call_next(request)
        return response
