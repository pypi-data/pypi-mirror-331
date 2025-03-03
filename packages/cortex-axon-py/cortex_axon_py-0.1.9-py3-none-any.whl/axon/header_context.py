import contextvars

# This context variable will hold the inbound headers.
inbound_headers_var = contextvars.ContextVar("inbound_headers", default={})
