from jose import JWTError, jwt, ExpiredSignatureError
from OpenSSL import crypto
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from provider_app.config import get_settings

settings = get_settings()

PUB_KEY_PATH = settings.PUB_KEY_PATH
ALGORITHM = settings.ALGORITHM

def _get_public_key(filepath: str) -> bytes:
    """
    Extracts and returns the public key from a PEM-encoded certificate file.

    Args:
        filepath (str): The path to the PEM-encoded certificate file.

    Returns:
        bytes: The public key in PEM format.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        OpenSSL.crypto.Error: If the certificate cannot be loaded or parsed.
    """
    with open(filepath, "rb") as cert_file:
        cert = cert_file.read()

    cert_obj = crypto.load_certificate(crypto.FILETYPE_PEM, cert)
    pub_key_obj = cert_obj.get_pubkey()
    return crypto.dump_publickey(crypto.FILETYPE_PEM, pub_key_obj)

security = HTTPBearer()

PUB_KEY = _get_public_key(PUB_KEY_PATH)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> None:
    """
    Verifies the validity of a JWT token provided via HTTP Authorization credentials.

    Decodes the token using the public key and specified algorithm. Raises an HTTP 401 Unauthorized
    exception if the token is expired or invalid.

    Args:
        credentials (HTTPAuthorizationCredentials): The HTTP authorization credentials containing the JWT token.

    Raises:
        HTTPException: If the token is expired or invalid, with appropriate error details.
    """
    token = credentials.credentials
    try:
        jwt.decode(token, PUB_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
