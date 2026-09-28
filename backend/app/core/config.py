import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    PROJECT_NAME: str = "PRIVASCOPE"
    VERSION: str = "2.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Environment & Database
    ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./privascope.db"
    
    # Security
    JWT_SECRET: str = "privascope-dev-only-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Google OAuth 2.0 / OpenID Connect
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # AI Privacy Gateway
    DEFAULT_GATEWAY_PROVIDER: str = "local_demo"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GATEWAY_SESSION_TTL_MINUTES: int = 30
    
    # Storage
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage"
    UPLOADS_DIR: Path = STORAGE_DIR / "uploads"
    PROTECTED_DIR: Path = STORAGE_DIR / "protected"
    TEMP_DIR: Path = STORAGE_DIR / "temp"
    
    # File Policies
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: set[str] = {"pdf", "docx", "xlsx", "csv", "txt", "png", "jpg", "jpeg"}
    
    # Retention (hours)
    TEMP_FILE_RETENTION_HOURS: int = 24
    
    # Risk Engine Default Weights (Product Policy Weights)
    WEIGHT_AADHAAR: float = 10.0
    WEIGHT_PAN: float = 8.0
    WEIGHT_BANK_ACCOUNT: float = 8.0
    WEIGHT_UPI: float = 7.0
    WEIGHT_IFSC: float = 5.0
    WEIGHT_PHONE: float = 4.0
    WEIGHT_EMAIL: float = 3.0
    WEIGHT_STUDENT_ID: float = 3.0

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        if not self.CORS_ORIGINS:
            return ["http://localhost:5173", "http://127.0.0.1:5173"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def normalized_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    @model_validator(mode="after")
    def validate_production_security(self):
        insecure_defaults = {
            "privascope-dev-only-secret-key-change-in-production",
            "privascope-secure-jwt-secret-key-production-ready-2026",
            "secret",
            "changeme",
            "dev-secret",
            "privascope-secret"
        }
        if self.ENV == "production":
            if not self.JWT_SECRET or self.JWT_SECRET in insecure_defaults or len(self.JWT_SECRET) < 32:
                raise ValueError(
                    "FATAL SECURITY ERROR: In production (ENV=production), a strong, random "
                    "JWT_SECRET of at least 32 characters must be explicitly supplied via environment variables."
                )
        return self

settings = Settings()

# Ensure directories exist
for path in [settings.STORAGE_DIR, settings.UPLOADS_DIR, settings.PROTECTED_DIR, settings.TEMP_DIR]:
    path.mkdir(parents=True, exist_ok=True)
