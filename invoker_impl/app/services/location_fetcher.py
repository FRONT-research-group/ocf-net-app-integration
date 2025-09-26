import asyncio

from app.utils.helper import build_send_http_request, build_monitoring_event_subscription, extract_callback_url
from app.config import get_settings

settings = get_settings()

async def send_net_req_and_loc_notification(url,access_token_file_path, payload: dict) -> None:
    try:
        monitoring_event_request_body = build_monitoring_event_subscription(payload)
        resp = await build_send_http_request(url, access_token_file_path, monitoring_event_request_body.model_dump())
        print(f"Response from NET: {resp.status_code}, {resp.json()}")
        callback_url = extract_callback_url(payload)
        xapp_response_body = resp.json()
        await build_send_http_request(callback_url, None, xapp_response_body)
    except asyncio.CancelledError:
        print("Task was cancelled")


async def get_location(payload: dict) -> None:
    url = settings.url
    access_token_file_path = settings.access_token_file_path
    asyncio.create_task(send_net_req_and_loc_notification(url,access_token_file_path, payload))
    return None