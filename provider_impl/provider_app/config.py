from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8080
    # log_directory_path: str = "./app/log/"
    # log_filename_path: str = f"{log_directory_path}app_logger"
    PUB_KEY_PATH: str | None = None
    ALGORITHM: str = "RS256"

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()

def get_settings() -> Settings:
    return settings