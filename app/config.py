from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict


class TortoiseORMSettings(BaseSettings):
    db_connection: str = "sqlite://db.sqlite3"
    apps_models_models: str = "app.models"
    apps_models_default_connection: str = "default"
    


class JWTSettings(BaseSettings):
    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1000
    refresh_token_expire_days: int = 30


class SMSSettings(BaseSettings):
    sms_ir_auth_token: str = (
        "KPhpaDjO3PGzUOopstREA0XydbXfzUY9vl00t4Mt7bw7CwLxV613vtV9Qfqp7fZy"
    )
    sms_ir_template_id: int = 691447
    twilio_account_sid: str = "AC3f6250bbbf612b3ca294893f83ac4c86"
    twilio_auth_token: str = "f0d8e6e6e2017976daaa9317df0b4bf3"
    twilio_number: str = "+16476974100"


class OTPSettings(BaseSettings):
    digits: int = 6
    interval: int = 21212
    resend_timeout: int = 60


class Settings(BaseSettings):
    encryption_key: bytes = b"TMWqqeqUi9Ip8vRz7iuc0O16BC6XY-FUOBbOEl-zvog="
    password_hash_secret: bytes = b"your_secret_key_here"
    tortoise_orm: TortoiseORMSettings = TortoiseORMSettings()
    jwt: JWTSettings = JWTSettings()
    sms: SMSSettings = SMSSettings()
    otp: OTPSettings = OTPSettings()


# Now you can load the settings


settings = Settings()
