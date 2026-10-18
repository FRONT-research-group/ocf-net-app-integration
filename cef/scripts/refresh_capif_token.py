#!/usr/bin/env python3

import os
import sys

from capif_compat import install_capif_compat
from opencapif_sdk import service_discoverer


install_capif_compat()


def main():
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: refresh_capif_token.py <token-output-file>"
        )

    config_file = os.environ.get("INVOKER_CONFIG_FILE")

    if not config_file:
        raise SystemExit(
            "ERROR: INVOKER_CONFIG_FILE is not set"
        )

    token_file = sys.argv[1]

    discoverer = service_discoverer(
        config_file=config_file
    )

    print("Running CAPIF service discovery...")
    discoverer.discover()

    print("Requesting CAPIF access token...")
    discoverer.get_tokens()

    token = discoverer.token

    if not token:
        raise SystemExit("ERROR: CAPIF returned no token")

    with open(token_file, "w") as file:
        file.write(token)

    os.chmod(token_file, 0o600)

    print("Discovery: OK")
    print("CAPIF JWT: received")
    print("JWT length:", len(token))


if __name__ == "__main__":
    main()
