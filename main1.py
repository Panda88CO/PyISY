
from __future__ import annotations
import asyncio
import logging
from urllib.parse import urlparse
import argparse
import asyncio
import logging
import time
from urllib.parse import urlparse

from pyisy import ISY
from pyisy.connection import ISYConnectionError, ISYInvalidAuthError, get_new_client_session
from pyisy.constants import NODE_CHANGED_ACTIONS, SYSTEM_STATUS
from pyisy.logging import LOG_VERBOSE, enable_logging
from pyisy.nodes import NodeChangedEvent

from pyisy import ISY
from pyisy.connection import ISYConnectionError, ISYInvalidAuthError, get_new_client_session

try:
    import udi_interface
    logging = udi_interface.LOGGER
    Custom = udi_interface.Custom
    Interface = udi_interface.Interface
except ImportError:
    import logging
    logging.basicConfig(level=30)
_LOGGER = logging.getLogger(__name__)

"""Validate the user input allows us to connect."""


user = "Panda88"
password = "coe123COE"
host = urlparse("http://192.168.1.204:80/")
tls_version = "1.2" # Can be False if using HTTP

if host.scheme == "http":
    https = False
    port = host.port or 80
elif host.scheme == "https":
    https = True
    port = host.port or 443
else:
    _LOGGER.error("host value in configuration is invalid.")
    #return False

# Use the helper function to get a new aiohttp.ClientSession.
websession = get_new_client_session(https, tls_version)

# Connect to ISY controller.
isy_conn = ISY(
    host.hostname,
    port,
    user,
    password,
    use_https=https,
    tls_ver=tls_version,
    webroot=host.path,
    websession=websession,
)

print(isy_conn)

async def main(url, username, password, tls_ver):
    """Execute connection to ISY and load all system info."""
    _LOGGER.info("Starting PyISY...")
    t0 = time.time()
    host = urlparse(url)
    if host.scheme == "http":
        https = False
        port = host.port or 80
    elif host.scheme == "https":
        https = True
        port = host.port or 443
    else:
        _LOGGER.error("host value in configuration is invalid.")
        return False

    # Use the helper function to get a new aiohttp.ClientSession.
    websession = get_new_client_session(https, tls_ver)

    # Connect to ISY controller.
    isy = ISY(
        host.hostname,
        port,
        username=username,
        password=password,
        use_https=https,
        tls_ver=tls_ver,
        webroot=host.path,
        websession=websession,
        use_websocket=True,
    )

    try:
        await isy.initialize()
    except (ISYInvalidAuthError, ISYConnectionError):
        _LOGGER.error(
            "Failed to connect to the ISY, please adjust settings and try again."
        )
        await isy.shutdown()
        return
    except Exception as err:
        _LOGGER.error("Unknown error occurred: %s", err.args[0])
        await isy.shutdown()
        raise

    # Print a representation of all the Nodes
    _LOGGER.debug(repr(isy.nodes))
    _LOGGER.info("Total Loading time: %.2fs", time.time() - t0)

    try:
        isy.websocket.start()
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        await isy.shutdown()