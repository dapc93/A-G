from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql+psycopg://ag_crm:ag_crm@localhost:5432/ag_crm"

    SECRET_KEY: str = "cambiar-en-produccion-0000000000000000000000000000"
    JWT_SECRET_KEY: str = "cambiar-en-produccion-0000000000000000000000000000"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 10080  # 7 dias

    ALLOWED_ORIGINS: str = "http://localhost:3000"

    STOCK_BAJO_UMBRAL: int = 3

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


settings = Settings()
