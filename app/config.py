

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_hostname: str
    database_port:str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    razorpay_key_id: str
    razorpay_key_secret: str
    RAZORPAY_WEBHOOK_SECRET: str
    WEBHOOK_URL: str

    class Config():
        env_file = ".env"

settings = Settings()
