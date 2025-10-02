''''Main entry point for the FastAPI application.
'''
from fastapi import FastAPI

from app.routers import location_fetch
from app.config import get_settings
from app.utils.logger import get_app_logger

settings = get_settings()

logger = get_app_logger()
logger.info("Starting INVOKER APP")
logger.info("Host: %s, Port: %s", settings.invoker_host, settings.invoker_port)
logger.info("Log Directory Path: %s", settings.invoker_log_directory_path)
logger.info("Log Filename Path: %s", settings.invoker_log_filename_path)
logger.info("Provider Target URL: %s", settings.provider_target_url)
logger.info("Invoker Access Token File: %s", settings.invoker_access_token_file)



app = FastAPI()

app.include_router(location_fetch.router, prefix="/invoker-app/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.invoker_host, port=settings.invoker_port)
