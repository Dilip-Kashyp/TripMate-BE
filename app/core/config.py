from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "TripMate AI"
    
    # RapidAPI (IRCTC)
    RAPIDAPI_KEY: str
    RAPIDAPI_HOST: str = "irctc1.p.rapidapi.com"
    
    # Gemini API
    GEMINI_API_KEY: str
    
    # CORS
    CORS_ORIGINS: list = ["*"]

    # Extra settings from .env
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    LLM_TEMPERATURE: float = 0.7
    MAX_TRAINS_TO_ANALYZE: int = 10
    TOOL_TIMEOUT_SECONDS: int = 15
    REQUEST_TIMEOUT_SECONDS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
