from pathlib import Path

from scripts.generate_keys import generate_missing_key_pairs


def test_generate_missing_key_pairs_does_not_overwrite_existing_keys(tmp_path: Path):
    key_paths = {
        "admin_private": tmp_path / "admin_private_key.pem",
        "admin_public": tmp_path / "admin_public_key.pem",
        "system_private": tmp_path / "system_private_key.pem",
        "system_public": tmp_path / "system_public_key.pem",
    }
    for path in key_paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("existing-key", encoding="utf-8")

    result = generate_missing_key_pairs(
        admin_private_key_path=key_paths["admin_private"],
        admin_public_key_path=key_paths["admin_public"],
        system_private_key_path=key_paths["system_private"],
        system_public_key_path=key_paths["system_public"],
    )

    assert result is False
    for path in key_paths.values():
        assert path.read_text(encoding="utf-8") == "existing-key"


def test_generate_missing_key_pairs_creates_all_keys_when_all_keys_are_missing(tmp_path: Path):
    key_paths = {
        "admin_private": tmp_path / "admin_private_key.pem",
        "admin_public": tmp_path / "admin_public_key.pem",
        "system_private": tmp_path / "system_private_key.pem",
        "system_public": tmp_path / "system_public_key.pem",
    }

    result = generate_missing_key_pairs(
        admin_private_key_path=key_paths["admin_private"],
        admin_public_key_path=key_paths["admin_public"],
        system_private_key_path=key_paths["system_private"],
        system_public_key_path=key_paths["system_public"],
    )

    assert result is True
    assert all(path.exists() for path in key_paths.values())


def test_generate_missing_key_pairs_refuses_partial_key_sets_without_force(tmp_path: Path):
    existing_private = tmp_path / "admin_private_key.pem"
    existing_private.write_text("existing-private", encoding="utf-8")

    try:
        generate_missing_key_pairs(
            admin_private_key_path=existing_private,
            admin_public_key_path=tmp_path / "admin_public_key.pem",
            system_private_key_path=tmp_path / "system_private_key.pem",
            system_public_key_path=tmp_path / "system_public_key.pem",
        )
    except RuntimeError as exc:
        assert "partial RSA key set" in str(exc)
    else:
        raise AssertionError("Partial key sets must not be regenerated implicitly")

    assert existing_private.read_text(encoding="utf-8") == "existing-private"
