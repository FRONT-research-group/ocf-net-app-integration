from fastapi import APIRouter, status


from app.schemas.location_fetch import LocationRequset
from app.services import location_fetcher as loc_service
from app.invoker_onboarding.invoker_capif_connector import onboard_invoker
from app.utils.logger import get_app_logger

logger = get_app_logger(__name__)

router = APIRouter()
invoices_callback_router = APIRouter()

@invoices_callback_router.post("{$request.body.notificationDestination}", description="No Content (successful notification)", response_model=None)
async def send_notification(callback_url: str) -> None:
    '''Exposure for Swagger Documentation'''

@router.post(
        "/location",
        description="Get a location for an imsi",
        tags=["Location Fetch API"],
        responses={status.HTTP_202_ACCEPTED: {"model": dict, "description": "Request is being processed"}},
        response_model_exclude_unset=True,
        callbacks=invoices_callback_router.routes)
async def get_location(loc_req: LocationRequset) -> None:
    """
    Asynchronously fetches location information based on the provided location request.

    Args:
        loc_req (LocationRequset): The location request object containing parameters for location retrieval.

    Returns:
        None: This function does not return anything explicitly.

    Raises:
        Any exceptions raised by onboard_invoker or loc_service.get_location.
    """
    jwt_token = onboard_invoker()
    logger.info("Obtained JWT Token: %s", jwt_token)
    payload = loc_req.model_dump()
    return await loc_service.get_location(payload, jwt_token)
