from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache
from typing import List


# Known insecure defaults — must never be used in production
_INSECURE_SECRET_PATTERNS = (
    "",
    "your-secret-key-change-this-in-production",
    "your-secret-key-change-in-production",
    "your-refresh-secret-key-change-in-production",
    "change-me",
    "secret",
)


class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = "postgresql://apexasset:apexasset123@localhost:5432/apexasset_db"
    DATABASE_ASYNC_URL: str = "postgresql+asyncpg://apexasset:apexasset123@localhost:5432/apexasset_db"
    # Read replica for reports/dashboard (optional). If empty, primary is used for both read and write.
    DATABASE_READ_ASYNC_URL: str = ""
    
    # InfluxDB Configuration
    INFLUXDB_URL: str = "http://localhost:8086"
    INFLUXDB_TOKEN: str = ""
    INFLUXDB_ORG: str = "apexasset"
    INFLUXDB_BUCKET: str = "sensor_data"
    
    # Application Configuration — JWT keys MUST be set via env in production
    SECRET_KEY: str = ""
    REFRESH_SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"
    
    # Cache (dashboard)
    DASHBOARD_CACHE_TTL_SECONDS: int = 10
    REDIS_URL: str = ""  # e.g. redis://localhost:6379/0 — if set, Redis is used

    # MQTT (optional; for real-time sensor/alert ingestion)
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883

    # API base URL (for health/websocket URL in responses)
    API_BASE_URL: str = "http://localhost:8000"
    
    # Environment
    ENVIRONMENT: str = "development"

    # Rate limiting (e.g. "5/minute", "100/hour")
    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_REGISTER: str = "3/minute"
    RATE_LIMIT_REFRESH: str = "10/minute"
    RATE_LIMIT_DEFAULT: str = ""  # Empty = no default limit; set e.g. "60/minute" for global limit

    @property
    def websocket_url(self) -> str:
        """WebSocket URL derived from API_BASE_URL."""
        base = self.API_BASE_URL.strip()
        return base.replace("http://", "ws://").replace("https://", "wss://").rstrip("/") + "/ws"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @model_validator(mode="after")
    def validate_jwt_secrets(self) -> "Settings":
        """Reject insecure or missing JWT keys, especially in production."""
        sk = (self.SECRET_KEY or "").strip()
        rsk = (self.REFRESH_SECRET_KEY or "").strip()

        if self.ENVIRONMENT == "production":
            if not sk or sk in _INSECURE_SECRET_PATTERNS or len(sk) < 32:
                raise ValueError(
                    "SECRET_KEY must be set via env (min 32 chars) in production. "
                    "Example: openssl rand -hex 32"
                )
            if not rsk or rsk in _INSECURE_SECRET_PATTERNS or len(rsk) < 32:
                raise ValueError(
                    "REFRESH_SECRET_KEY must be set via env (min 32 chars) in production. "
                    "Example: openssl rand -hex 32"
                )
        else:
            if not sk or not rsk or sk in _INSECURE_SECRET_PATTERNS or rsk in _INSECURE_SECRET_PATTERNS:
                raise ValueError(
                    "SECRET_KEY and REFRESH_SECRET_KEY must be set in .env (no default). "
                    "Example: openssl rand -hex 32"
                )
        return self
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
