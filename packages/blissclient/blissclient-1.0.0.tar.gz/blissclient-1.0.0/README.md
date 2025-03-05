# blissclient

A python client for the BLISS REST API, the high-level client is fully typed ready for auto-completion in any modern IDE.


## Getting Started

Set the `BLISSAPI_URL`

```bash
export BLISSAPI_URL=http://localhost:5000
```

Then:

```python
from blissclient import BlissClient

client = BlissClient()

omega = client.hardware.get("omega")
print(omega.position)

future = omega.move(100)
# Wait for the call to temrinate, blocking
future.get()
```

Execute calls in the session:

```python
import time
from blissclient import BlissClient, get_object

client = BlissClient()

test_session = client.session
future = test_session.call("ascan", get_object("omega"), 0, 10, 10, 0.1, get_object("diode"))

# Ask for the current future state
print(future.state)

# Block until terminated
result = future.get()

# The redis scan key, can be used with `blissdata``
print(result["key"])
```

get_object("<name>") are translated to the relevant beacon objects.

See the test suite for more examples.
