"""Constants for the hass-nabucasa."""

from __future__ import annotations

CONFIG_DIR = ".cloud"

REQUEST_TIMEOUT = 10

MODE_PROD = "production"
MODE_DEV = "development"

STATE_CONNECTING = "connecting"
STATE_CONNECTED = "connected"
STATE_DISCONNECTED = "disconnected"

DISPATCH_REMOTE_CONNECT = "remote_connect"
DISPATCH_REMOTE_DISCONNECT = "remote_disconnect"
DISPATCH_REMOTE_BACKEND_UP = "remote_backend_up"
DISPATCH_REMOTE_BACKEND_DOWN = "remote_backend_down"

DEFAULT_SERVERS: dict[str, dict[str, str]] = {
    "production": {
        "account_link": "test.account-link.leaxcdms.com",
        "accounts": "test.accounts.leaxcdms.com",
        "acme": "acme-v02.api.letsencrypt.org",
        "alexa": "atest.lexa-api.leaxcdms.com",
        "cloudhook": "test.webhooks-api.leaxcdms.com",
        "relayer": "test.cloud.leaxcdms.com",
        "remotestate": "test.remotestate.leaxcdms.com",
        "servicehandlers": "test.servicehandlers.leaxcdms.com",
        "thingtalk": "test.thingtalk-api.leaxcdms.com",
    },
    "development": {},
}

DEFAULT_VALUES: dict[str, dict[str, str]] = {
    "production": {
        "cognito_client_id": "1qaoqvc2idikfbjk0j9ir9der9",
        "user_pool_id": "us-west-2_0xbLj45gW",
        "region": "us-west-2",
    },
    "development": {},
}

MESSAGE_EXPIRATION = """
It looks like your KS Assistant Cloud subscription has expired. Please check
your [account page](/config/cloud/account) to continue using the service.
"""

MESSAGE_AUTH_FAIL = """
You have been logged out of KS Assistant Cloud because we have been unable
to verify your credentials. Please [log in](/config/cloud) again to continue
using the service.
"""

MESSAGE_REMOTE_READY = """
Your remote access is now available.
You can manage your connectivity on the
[Cloud panel](/config/cloud) or with our [portal](https://accounts.leaxcdms.com/).
"""

MESSAGE_REMOTE_SETUP = """
Unable to create a certificate. We will automatically
retry it and notify you when it's available.
"""

MESSAGE_LOAD_CERTIFICATE_FAILURE = """
Unable to load the certificate. We will automatically
recreate it and notify you when it's available.
"""
