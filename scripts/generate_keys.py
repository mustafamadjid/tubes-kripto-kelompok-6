import sys
from argparse import ArgumentParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings
from app.services.crypto_service import generate_rsa_key_pair, save_key_pair


def generate_missing_key_pairs(
    admin_private_key_path: str | Path,
    admin_public_key_path: str | Path,
    system_private_key_path: str | Path,
    system_public_key_path: str | Path,
    *,
    force: bool = False,
) -> bool:
    key_paths = [
        Path(admin_private_key_path),
        Path(admin_public_key_path),
        Path(system_private_key_path),
        Path(system_public_key_path),
    ]
    existing_paths = [path for path in key_paths if path.exists()]

    if existing_paths and not force:
        if len(existing_paths) == len(key_paths):
            return False
        missing = ", ".join(str(path) for path in key_paths if not path.exists())
        raise RuntimeError(
            "Refusing to regenerate a partial RSA key set because it can invalidate existing votes. "
            f"Missing files: {missing}. Restore the missing key files or rerun with --force for a fresh election."
        )

    admin_private, admin_public = generate_rsa_key_pair()
    system_private, system_public = generate_rsa_key_pair()
    save_key_pair(admin_private, admin_public, admin_private_key_path, admin_public_key_path)
    save_key_pair(system_private, system_public, system_private_key_path, system_public_key_path)
    return True


def main() -> None:
    parser = ArgumentParser(description="Generate RSA key pairs for the e-voting demo.")
    parser.add_argument("--force", action="store_true", help="overwrite existing keys for a fresh election")
    args = parser.parse_args()

    generated = generate_missing_key_pairs(
        settings.admin_private_key_path,
        settings.admin_public_key_path,
        settings.system_private_key_path,
        settings.system_public_key_path,
        force=args.force,
    )
    if generated:
        print("RSA key pairs generated in app/keys")
    else:
        print("RSA key pairs already exist; keeping existing keys")


if __name__ == "__main__":
    main()
