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

    # Google OAuth
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    # Base URL aplikasi, contoh: http://localhost:8000 atau https://evoting.itera.ac.id
    app_base_url: str = os.getenv("APP_BASE_URL", "http://localhost:8000")
    # Domain email yang diizinkan (pisah koma). Kosongkan = semua email boleh.
    allowed_email_domains: str = os.getenv("ALLOWED_EMAIL_DOMAINS", "student.itera.ac.id")
    # Email admin yang boleh login via Google (pisah koma)
    admin_google_emails: str = os.getenv("ADMIN_GOOGLE_EMAILS", "")

    # Mode operasi: "production" atau "demo"
    # production : hanya @student.itera.ac.id, NIM wajib 9 digit dari email
    # demo       : domain bebas, voter_id = seluruh username sebelum @ (tanpa angka wajib)
    oauth_mode: str = os.getenv("OAUTH_MODE", "production")


settings = Settings()
