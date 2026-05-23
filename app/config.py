import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "E-Voting RSA SHA-256")
    app_secret_key: str = os.getenv("APP_SECRET_KEY", "change-this-secret")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/evoting_db",
    )
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")
    admin_private_key_path: str = os.getenv("ADMIN_PRIVATE_KEY_PATH", "app/keys/admin_private_key.pem")
    admin_public_key_path: str = os.getenv("ADMIN_PUBLIC_KEY_PATH", "app/keys/admin_public_key.pem")
    system_private_key_path: str = os.getenv("SYSTEM_PRIVATE_KEY_PATH", "app/keys/system_private_key.pem")
    system_public_key_path: str = os.getenv("SYSTEM_PUBLIC_KEY_PATH", "app/keys/system_public_key.pem")
    enable_dev_routes: bool = os.getenv("ENABLE_DEV_ROUTES", "true").lower() == "true"


settings = Settings()
