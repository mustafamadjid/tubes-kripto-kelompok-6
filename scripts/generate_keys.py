import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings
from app.services.crypto_service import generate_rsa_key_pair, save_key_pair


def main() -> None:
    admin_private, admin_public = generate_rsa_key_pair()
    system_private, system_public = generate_rsa_key_pair()
    save_key_pair(admin_private, admin_public, settings.admin_private_key_path, settings.admin_public_key_path)
    save_key_pair(system_private, system_public, settings.system_private_key_path, settings.system_public_key_path)
    print("RSA key pairs generated in app/keys")


if __name__ == "__main__":
    main()
