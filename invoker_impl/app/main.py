''''Main entry point for the FastAPI application.
'''
from fastapi import FastAPI

from app.routers import location_fetch
from app.config import get_settings
from app.utils.logger import get_app_logger

settings = get_settings()

logger = get_app_logger()
logger.info("Starting NEF Monitoring Event API")
logger.info("Host: %s, Port: %s", settings.host, settings.port)



app = FastAPI()

app.include_router(location_fetch.router, prefix="/invoker-app/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
