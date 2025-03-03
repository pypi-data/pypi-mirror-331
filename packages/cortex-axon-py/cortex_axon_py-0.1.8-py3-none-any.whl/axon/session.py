import contextvars
from .header_context import inbound_headers_var
import requests
from requests import Session

inbound_headers_var = contextvars.ContextVar("inbound_headers", default={})

def capture_inbound_headers(headers):
    inbound_headers_var.set(dict(headers))

_original_request = requests.Session.request

def _forwarding_request(self, method, url, **kwargs):
    headers_to_forward = inbound_headers_var.get()
    if headers_to_forward:
        headers_to_forward = dict(headers_to_forward)
        headers_to_forward.pop("Host", None)
        
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        for k, v in headers_to_forward.items():
            if k not in kwargs["headers"]:
                kwargs["headers"][k] = v

    return _original_request(self, method, url, **kwargs)

def patch_requests():
    Session.request = _forwarding_request
