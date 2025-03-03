## Flask

```
from axon.integrations import setup_flask_auto_header_forwarding

app = Flask(__name__)
setup_flask_auto_header_forwarding(app)
```

## Django
In your Django project’s settings.py, add the provided middleware:

In your Django project’s **settings.py**
```
MIDDLEWARE = [
    # ... other middleware ...
    'axon.integrations.DjangoCaptureHeadersMiddleware',
]
```

And ensure you call patch_requests() somewhere at startup (for example, in your app’s apps.py ready method)
```
from axon.session import patch_requests
patch_requests()
```

## FastAPI

The integration with FastAPI requires starlette. You will need to install cortex-axon-py using the following command
```
pip install cortex-axon-py[fastapi]
```

```
from fastapi import FastAPI
from axon.integrations import FastAPICaptureHeadersMiddleware
from axon.session import patch_requests

app = FastAPI()

# Add the middleware
app.add_middleware(FastAPICaptureHeadersMiddleware)

# Optionally patch requests for auto header forwarding
patch_requests()
```
