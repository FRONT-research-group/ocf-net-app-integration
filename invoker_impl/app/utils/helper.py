'''helper class to build and send http request'''
import httpx

from app.utils.exceptions import TokenFileError
from app.schemas.location_fetch import MonitoringEventSubscriptionRequest, MonitoringType, LocationType
from app.utils.logger import get_app_logger

log = get_app_logger()

def build_monitoring_event_subscription(xapp_payload_request: dict
    ) -> MonitoringEventSubscriptionRequest:
    """Builds a MonitoringEventSubscriptionRequest from the given xApp payload."""
        
    return MonitoringEventSubscriptionRequest(
        msisdn=xapp_payload_request["msisdn"].lstrip("+"),
        notificationDestination=xapp_payload_request["notificationDestination"],
        monitoringType=MonitoringType.LOCATION_REPORTING,
        locationType=LocationType.LAST_KNOWN
    )


def extract_callback_url(xapp_payload_request: dict) -> str:
    """Extracts the callback URL from the given xApp payload."""
    return xapp_payload_request["notificationDestination"]

def _read_access_token_from_file(file_path: str) -> str:
    """
    Reads an access token from a specified file.

    Args:
        file_path (str): The path to the file containing the access token.

    Returns:
        str: The access token read from the file.

    Raises:
        TokenFileError: If the file is not found or an I/O error occurs while reading the file.
    """
    try:
        with open(file_path, "r", encoding='utf-8') as file:
            token = file.read().strip()
            return token
    except FileNotFoundError as exc:
        raise TokenFileError(f"Token file not found: {file_path}") from exc
    except IOError as exc:
        raise TokenFileError(f"Error reading token file: {exc}") from exc
        
async def build_send_http_request(url : str, access_token_path: str | None, payload: dict) -> httpx.Response:
    """
    Asynchronously builds and sends an HTTP POST request to the specified URL with an 
    authorization header.

    Args:
        url (str): The endpoint URL to send the POST request to.
        access_token_path (str): The path to the file containing the access token.

    Returns:
        None

    Side Effects:
        Prints the status code and JSON response of the HTTP request to the console.

    Raises:
        Any exceptions raised by httpx or file reading operations.
    """
    if access_token_path is not None:
        token = _read_access_token_from_file(access_token_path)

        headers = {
            "Authorization": token
        }
    else:
        headers = {}

    try:
        async with httpx.AsyncClient() as client:
            log.info("Sending POST request to %s with payload: %s and headers: %s",url,payload,headers)

            response = await client.post(url, headers=headers,json=payload)
            response.raise_for_status()
            
            print(f"Status Code: {response.status_code}")
            print("Success:", response.json())

            return response
    except httpx.TimeoutException:
        print("Request timed out.")
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code}: {exc.response.text}")
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}: {exc}")