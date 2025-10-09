from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    rapidapi_key: str
    rapidapi_host: str = "irctc1.p.rapidapi.com"
    
    class Config:
        env_file = ".env"

settings = Settings()
