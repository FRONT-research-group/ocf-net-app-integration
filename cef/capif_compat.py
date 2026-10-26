import json
import os
from urllib.parse import urlsplit, urlunsplit

import requests
import urllib3
from requests.auth import HTTPBasicAuth


_INSTALLED = False


def _bool(value, default=True):
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _decode_payload(kwargs):
    payload = kwargs.get("json")

    if payload is None:
        payload = kwargs.get("data", {})

    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except Exception:
            payload = {}

    return payload if isinstance(payload, dict) else {}


def install_capif_compat():
    global _INSTALLED

    if _INSTALLED:
        return

    _INSTALLED = True

    real_request = requests.sessions.Session.request

    capif_host = os.getenv("CAPIF_HOST", "")
    register_host = os.getenv("REGISTER_HOST", "")
    register_port = os.getenv("CAPIF_REGISTER_PORT", "8084")

    getauth_mode = os.getenv(
        "CAPIF_GETAUTH_MODE",
        "basic_get"
    ).lower()

    tls_verify = _bool(
        os.getenv("CAPIF_TLS_VERIFY"),
        True
    )

    ca_file = os.getenv("CAPIF_CA_FILE", "").strip()

    if not tls_verify:
        urllib3.disable_warnings(
            urllib3.exceptions.InsecureRequestWarning
        )

    def compat_request(self, method, url, **kwargs):
        parsed = urlsplit(url)

        # Current CAPIF Register deployment:
        # GET /getauth using HTTP Basic authentication.
        if (
            parsed.path.rstrip("/").endswith("/getauth")
            and getauth_mode == "basic_get"
        ):
            payload = _decode_payload(kwargs)

            method = "GET"

            netloc = (
                f"{register_host}:{register_port}"
                if register_host
                else parsed.netloc
            )

            url = urlunsplit((
                "https",
                netloc,
                parsed.path,
                parsed.query,
                parsed.fragment,
            ))

            kwargs.pop("json", None)
            kwargs.pop("data", None)

            # Invoker SDK sends credentials in the request payload.
            # Provider SDK already supplies HTTPBasicAuth directly.
            # Preserve existing auth when no payload credentials exist.
            username = payload.get("username")
            password = payload.get("password")

            if username is not None or password is not None:
                kwargs["auth"] = HTTPBasicAuth(
                    username or "",
                    password or ""
                )

        target = urlsplit(url).hostname

        if target in {capif_host, register_host}:
            if ca_file:
                kwargs["verify"] = ca_file
            else:
                kwargs["verify"] = tls_verify

        return real_request(
            self,
            method,
            url,
            **kwargs
        )

    requests.sessions.Session.request = compat_request
