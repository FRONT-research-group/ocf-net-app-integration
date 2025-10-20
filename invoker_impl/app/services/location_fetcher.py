import asyncio, uuid

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from app.utils.helper import build_send_http_request, build_monitoring_event_subscription, extract_callback_url
from app.config import get_settings
from app.utils.logger import get_app_logger
from app.dependencies import get_task_registry, get_callback_data_queue

log = get_app_logger(__name__)

settings = get_settings()

task_registry = get_task_registry()

callback_data_queue = get_callback_data_queue()

async def send_net_req_and_loc_notification(url,jwt_token :str, payload: dict, task_id: str) -> None:
    """
    Sends a network request and location notification asynchronously.

    This function builds a monitoring event subscription request from the given payload,
    sends it to the specified URL, and then sends the response to a callback URL extracted
    from the payload. Handles HTTP exceptions and task cancellation by sending error
    notifications to the callback URL and logging errors. Removes the task from the registry
    upon completion.

    Args:
        url (str): The endpoint URL to send the monitoring event subscription request.
        access_token_file (str): Path to the access token file for authentication.
        payload (dict): The payload containing data for the monitoring event subscription.
        task_id (str): Unique identifier for the asynchronous task.

    Raises:
        HTTPException: If the HTTP request fails.
        asyncio.CancelledError: If the task is cancelled.
    """
    callback_url = extract_callback_url(payload)
    monitoring_event_request_body = build_monitoring_event_subscription(payload,settings.current_loc_enabled)
    log.info("Constructed monitoring event request body: %s", monitoring_event_request_body)
    try:
        log.info("Sending monitoring event subscription request to %s with request body %s", url, monitoring_event_request_body)
        resp = await build_send_http_request(url, jwt_token, monitoring_event_request_body.model_dump(mode='json',exclude_none=True, by_alias=True),task_id)
        if settings.current_loc_enabled:
            log.info("Current location reporting is enabled, waiting for callback data...")
            counter : int = 0
            while counter < settings.current_loc_max_num_reports:
                counter += 1
                xapp_response_body = await callback_data_queue.get()
                log.info("Sending response to callback URL %s with body %s", str(callback_url), xapp_response_body)
                await build_send_http_request(str(callback_url), None, xapp_response_body,task_id)
        else:
            log.info("Last known location reporting is enabled, proceeding with immediate data report.")
            xapp_response_body = resp.json()
            log.info("Sending response to callback URL %s with body %s", str(callback_url), xapp_response_body)
            await build_send_http_request(str(callback_url), None, xapp_response_body,task_id)
    except HTTPException as exc:
        log.error("Error response %s: %s", exc.status_code, exc.detail)
        error_payload = {
            "status": "failed",
            "code": exc.status_code,
            "detail": exc.detail
        }
        await build_send_http_request(str(callback_url), None, error_payload,task_id)
    except asyncio.CancelledError:
        log.error("Task was cancelled")
        error_payload = {
            "status": "failed",
            "code": 500,
            "detail": "Task was cancelled"
        }
    finally:
        task_registry.pop(task_id)
        log.info("Task registry after removal: %s", task_registry)


async def get_location(payload: dict, jwt_token: str) -> None:
    """
    Asynchronously initiates a location fetch request by creating a background task to send a network request and notification.
    Stores the task in a registry using a generated UUID and returns an HTTP 202 response with the task ID.

    Args:
        payload (dict): The payload containing data required for the location fetch request.

    Returns:
        JSONResponse: HTTP 202 Accepted response with a message and the generated task ID.
    """
    url = settings.provider_target_url
    # access_token_file = settings.invoker_access_token_file
    task_uuid = str(uuid.uuid4())
    task = asyncio.create_task(send_net_req_and_loc_notification(url,jwt_token, payload,str(task_uuid)))

    task_registry[task_uuid] = task

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"message": "Request is being processed", "task_id": task_uuid},
    )    