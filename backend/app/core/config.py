from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./fixedincome.db"
    treasury_base_url: str = (
        "https://home.treasury.gov/resource-center/"
        "data-chart-center/interest-rates/pages/xml"
    )
    cors_origins: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
