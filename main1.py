
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
websession = get_new_client_session(https, tls_ver)

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
'''
try:
    with async_timeout.timeout(30):
        isy_conf_xml = await isy_conn.test_connection()
except (ISYInvalidAuthError, ISYConnectionError):
    _LOGGER.error(
        "Failed to connect to the ISY, please adjust settings and try again."
    )




_LOGGER = logging.getLogger(__name__)


async def main(url, username, password, tls_ver, events, node_servers):
    """Execute connection to ISY and load all system info."""
    _LOGGER.info("Starting PyISY...")
    t_0 = time.time()
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
        await isy.initialize(node_servers)
    except (ISYInvalidAuthError, ISYConnectionError):
        _LOGGER.exception("Failed to connect to the ISY, please adjust settings and try again.")
        await isy.shutdown()
        return None
    except Exception as err:
        _LOGGER.exception("Unknown error occurred: %s", err.args[0])
        await isy.shutdown()
        raise

    # Print a representation of all the Nodes
    _LOGGER.debug(repr(isy.nodes))
    _LOGGER.info("Total Loading time: %.2fs", time.time() - t_0)

    node_changed_subscriber = None
    system_status_subscriber = None

    def node_changed_handler(event: NodeChangedEvent) -> None:
        """Handle a node changed event sent from Nodes class."""
        (event_desc, _) = NODE_CHANGED_ACTIONS[event.action]
        _LOGGER.info(
            "Subscriber--Node %s Changed: %s %s",
            event.address,
            event_desc,
            event.event_info if event.event_info else "",
        )

    def system_status_handler(event: str) -> None:
        """Handle a system status changed event sent ISY class."""
        _LOGGER.info("System Status Changed: %s", SYSTEM_STATUS.get(event))

    try:
        if events:
            isy.websocket.start()
            node_changed_subscriber = isy.nodes.status_events.subscribe(node_changed_handler)
            system_status_subscriber = isy.status_events.subscribe(system_status_handler)
        await asyncio.Event.wait()
    except asyncio.CancelledError:
        pass
    finally:
        if node_changed_subscriber:
            node_changed_subscriber.unsubscribe()
        if system_status_subscriber:
            system_status_subscriber.unsubscribe()
        await isy.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=__package__)
    parser.add_argument("url", type=str)
    parser.add_argument("username", type=str)
    parser.add_argument("password", type=str)
    parser.add_argument("-t", "--tls-ver", dest="tls_ver", type=float)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-q", "--no-events", dest="no_events", action="store_true")
    parser.add_argument("-n", "--node-servers", dest="node_servers", action="store_true")
    parser.set_defaults(use_https=False, tls_ver=1.1, verbose=False)
    args = parser.parse_args()

    enable_logging(LOG_VERBOSE if args.verbose else logging.DEBUG)

    _LOGGER.info(
        "ISY URL: %s, username: %s, TLS: %s",
        args.url,
        args.username,
        args.tls_ver,
    )

    try:
        asyncio.run(
            main(
                url=args.url,
                username=args.username,
                password=args.password,
                tls_ver=args.tls_ver,
                events=(not args.no_events),
                node_servers=args.node_servers,
            )
        )
    except KeyboardInterrupt:
        _LOGGER.warning("KeyboardInterrupt received. Disconnecting!")
    '''