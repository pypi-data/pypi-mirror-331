from axon.session import capture_inbound_headers, patch_requests

try:
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
except ImportError as e:
    raise ImportError(
        "FastAPI integration requires 'starlette'. Install it with: pip install cortex-axon-py[fastapi]"
    ) from e

class AxonInstrument(BaseHTTPMiddleware):
    """
    FastAPI/Starlette middleware to capture inbound headers.
    Add this middleware to your FastAPI app.
    """
    async def dispatch(self, request: Request, call_next):
        capture_inbound_headers(dict(request.headers))
        response = await call_next(request)
        return response
