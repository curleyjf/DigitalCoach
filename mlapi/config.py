from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    AAPI_KEY: str
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(env_file=".env")
