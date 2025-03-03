import requests
from requests import Session
from .header_context import inbound_headers_var

# Save the original requests.Session.request method.
_original_request = requests.Session.request

def _forwarding_request(self, method, url, **kwargs):
    # Retrieve inbound headers from the context variable.
    headers_to_forward = inbound_headers_var.get()
    if headers_to_forward:
        # Remove the Host header if present.
        headers_to_forward = dict(headers_to_forward)
        headers_to_forward.pop("Host", None)
        
        # Ensure headers exist in kwargs.
        if "headers" not in kwargs:
            kwargs["headers"] = {}
        # Merge inbound headers with request-specific headers.
        for k, v in headers_to_forward.items():
            if k not in kwargs["headers"]:
                kwargs["headers"][k] = v

    return _original_request(self, method, url, **kwargs)

def patch_requests():
    """
    Monkey-patch requests.Session.request so that all outbound requests
    automatically include the headers stored in our context variable.
    """
    Session.request = _forwarding_request
