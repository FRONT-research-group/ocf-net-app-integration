'''Configuration settings for the application using Pydantic.'''
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8080
    log_directory_path: str = "./app/log/"
    log_filename_path: str = f"{log_directory_path}app_logger"
    url: str
    access_token_file_path: str = "./access_token.txt"

settings = Settings()

def get_settings() -> Settings:
    """
    Retrieve the current application settings.

    Returns:
        Settings: An instance containing the application's configuration settings.
    """
    return settings
