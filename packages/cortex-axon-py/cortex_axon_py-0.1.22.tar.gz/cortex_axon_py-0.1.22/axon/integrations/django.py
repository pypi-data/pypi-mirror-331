from axon.session import capture_inbound_headers, patch_requests

class AxonInstrument:
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
