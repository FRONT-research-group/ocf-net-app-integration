'''Configuration settings for the application using Pydantic.'''
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    invoker_host: str = "127.0.0.1"
    invoker_port: int = 8001
    invoker_log_directory_path: str = "./invoker_impl/logs/"
    invoker_log_filename_path: str = "./invoker_impl/logs/app_logger"
    provider_target_url:  str = "https://127.0.0.1:8000/3gpp-monitoring-event/v1/1/subscriptions"
    invoker_access_token_file: str = "./invoker_impl/invoker_folder/ppavlidis/jwt_token.txt"

settings = Settings()

def get_settings() -> Settings:
    """
    Retrieve the current application settings.

    Returns:
        Settings: An instance containing the application's configuration settings.
    """
    return settings
