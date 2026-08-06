from pydantic_settings import BaseSettings

APP_VERSION = "0.4.0"


class Settings(BaseSettings):
	DATABASE_URL: str = "postgresql+psycopg2://crm:crm_password@127.0.0.1:5432/crm_db"

	class Config:
		env_file = ".env"

settings = Settings()