import contextvars

inbound_headers_var = contextvars.ContextVar("inbound_headers", default={})
