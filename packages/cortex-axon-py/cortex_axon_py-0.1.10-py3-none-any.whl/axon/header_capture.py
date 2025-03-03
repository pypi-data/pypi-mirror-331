from .header_context import inbound_headers_var

def capture_inbound_headers(headers):
    inbound_headers_var.set(dict(headers))
