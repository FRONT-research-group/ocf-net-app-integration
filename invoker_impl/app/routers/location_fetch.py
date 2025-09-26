from fastapi import APIRouter, status, Request


from app.schemas.location_fetch import MonitoringEventReport
from app.services import location_fetcher as loc_service

router = APIRouter()
invoices_callback_router = APIRouter()

@invoices_callback_router.post("{$request.body.notificationDestination}", description="No Content (successful notification)", response_model=None)
async def send_notification(callback_url: str,) -> None:
    '''Exposure for Swagger Documentation'''
    pass

@router.post(
        "/location",
        description="Get a location for an imsi",
        tags=["Location Fetch API"],
        responses={status.HTTP_200_OK:{"model":MonitoringEventReport, "description": "200 OK"},
                   status.HTTP_404_NOT_FOUND: {"description":"404 Not Found"},},
        response_model_exclude_unset=True,
        callbacks=invoices_callback_router.routes)
async def get_location(request: Request) -> None:
    payload = await request.json()
    return await loc_service.get_location(payload)