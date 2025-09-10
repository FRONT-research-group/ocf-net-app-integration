from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8080

    TOKEN_PATH: str | None = None
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()

def get_settings() -> Settings:
    return settings