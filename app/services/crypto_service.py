from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey


def generate_rsa_key_pair() -> tuple[RSAPrivateKey, RSAPublicKey]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()


def save_key_pair(
    private_key: RSAPrivateKey,
    public_key: RSAPublicKey,
    private_path: str | Path,
    public_path: str | Path,
) -> None:
    private_path = Path(private_path)
    public_path = Path(public_path)
    private_path.parent.mkdir(parents=True, exist_ok=True)
    public_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    public_path.write_bytes(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


class CryptoService:
    def __init__(
        self,
        admin_private_key_path: str | Path,
        admin_public_key_path: str | Path,
        system_private_key_path: str | Path,
        system_public_key_path: str | Path,
    ) -> None:
        self.admin_private_key = self._load_private_key(admin_private_key_path)
        self.admin_public_key = self._load_public_key(admin_public_key_path)
        self.system_private_key = self._load_private_key(system_private_key_path)
        self.system_public_key = self._load_public_key(system_public_key_path)

    def encrypt_vote_plaintext(self, plaintext: str) -> bytes:
        return self.admin_public_key.encrypt(
            plaintext.encode("utf-8"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    def decrypt_vote_ciphertext(self, ciphertext: bytes) -> str:
        plaintext = self.admin_private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        return plaintext.decode("utf-8")

    def hash_ciphertext(self, ciphertext: bytes) -> str:
        digest = hashes.Hash(hashes.SHA256())
        digest.update(ciphertext)
        return digest.finalize().hex()

    def sign_hash(self, hash_hex: str) -> bytes:
        hash_bytes = bytes.fromhex(hash_hex)
        return self.system_private_key.sign(
            hash_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )

    def verify_signature(self, hash_hex: str, signature: bytes) -> bool:
        try:
            self.system_public_key.verify(
                signature,
                bytes.fromhex(hash_hex),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH,
                ),
                hashes.SHA256(),
            )
        except (InvalidSignature, ValueError):
            return False
        return True

    def verify_ciphertext_hash(self, ciphertext: bytes, expected_hash_hex: str) -> bool:
        return self.hash_ciphertext(ciphertext) == expected_hash_hex

    @staticmethod
    def _load_private_key(path: str | Path) -> RSAPrivateKey:
        key = serialization.load_pem_private_key(Path(path).read_bytes(), password=None)
        if not isinstance(key, RSAPrivateKey):
            raise TypeError("Expected RSA private key")
        return key

    @staticmethod
    def _load_public_key(path: str | Path) -> RSAPublicKey:
        key = serialization.load_pem_public_key(Path(path).read_bytes())
        if not isinstance(key, RSAPublicKey):
            raise TypeError("Expected RSA public key")
        return key
