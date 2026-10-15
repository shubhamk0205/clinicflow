from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ClinicFlow API"
    database_url: str = "postgresql+psycopg://clinicflow:clinicflow@localhost:5432/clinicflow"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
