from pathlib import Path

from app.services.crypto_service import CryptoService, generate_rsa_key_pair, save_key_pair


def create_crypto_service(tmp_path: Path) -> CryptoService:
    admin_private, admin_public = generate_rsa_key_pair()
    system_private, system_public = generate_rsa_key_pair()

    admin_private_path = tmp_path / "admin_private_key.pem"
    admin_public_path = tmp_path / "admin_public_key.pem"
    system_private_path = tmp_path / "system_private_key.pem"
    system_public_path = tmp_path / "system_public_key.pem"

    save_key_pair(admin_private, admin_public, admin_private_path, admin_public_path)
    save_key_pair(system_private, system_public, system_private_path, system_public_path)

    return CryptoService(
        admin_private_key_path=admin_private_path,
        admin_public_key_path=admin_public_path,
        system_private_key_path=system_private_path,
        system_public_key_path=system_public_path,
    )


def test_encrypt_decrypt_roundtrip(tmp_path):
    crypto = create_crypto_service(tmp_path)

    ciphertext = crypto.encrypt_vote_plaintext("nim:122140191|candidate_id:1|timestamp:2026-05-22T14:30:00+07:00")

    assert isinstance(ciphertext, bytes)
    assert crypto.decrypt_vote_ciphertext(ciphertext).startswith("nim:122140191")


def test_oaep_produces_different_ciphertext_for_same_plaintext(tmp_path):
    crypto = create_crypto_service(tmp_path)
    plaintext = "nim:122140191|candidate_id:1|timestamp:2026-05-22T14:30:00+07:00"

    first = crypto.encrypt_vote_plaintext(plaintext)
    second = crypto.encrypt_vote_plaintext(plaintext)

    assert first != second


def test_hash_and_signature_validation(tmp_path):
    crypto = create_crypto_service(tmp_path)
    ciphertext = crypto.encrypt_vote_plaintext("nim:122140191|candidate_id:1|timestamp:2026-05-22T14:30:00+07:00")

    hash_hex = crypto.hash_ciphertext(ciphertext)
    signature = crypto.sign_hash(hash_hex)

    assert len(hash_hex) == 64
    assert crypto.verify_signature(hash_hex, signature) is True
    assert crypto.verify_ciphertext_hash(ciphertext, hash_hex) is True
    assert crypto.verify_signature("0" * 64, signature) is False
    assert crypto.verify_signature(hash_hex, signature[:-1] + b"0") is False
    assert crypto.verify_ciphertext_hash(ciphertext + b"x", hash_hex) is False
