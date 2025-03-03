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

```
from fastapi import FastAPI
from axon.integrations import FastAPICaptureHeadersMiddleware
from axon.session import patch_requests

app = FastAPI()

app.add_middleware(FastAPICaptureHeadersMiddleware)

patch_requests()
```
