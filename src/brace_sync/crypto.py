"""Client-side encryption for vault objects.

The vault encrypts every payload before it reaches Cloudflare R2, GitHub, or
any other storage backend. This implementation avoids mandatory Python package
crypto dependencies by using Python's standard-library scrypt/HMAC primitives
and the system OpenSSL command for AES-256-CBC encryption.

The envelope uses encrypt-then-MAC: ciphertext and authenticated associated
data are verified with HMAC-SHA256 before any decryption is attempted.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Any

from .errors import EncryptionError

ENVELOPE_SCHEMA_VERSION = 1
ALGORITHM = "aes-256-cbc-hmac-sha256"
KDF = "scrypt"
SALT_BYTES = 16
IV_BYTES = 16
KEY_BYTES = 64
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1
OPENSSL = "openssl"


def _b64encode(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"), validate=True)


def canonical_json(value: Any) -> bytes:
    """Serialize JSON deterministically for authenticated associated data."""
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive encryption and authentication keys from a passphrase and salt."""
    if not passphrase:
        raise EncryptionError("A non-empty vault passphrase is required")
    return hashlib.scrypt(
        passphrase.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=KEY_BYTES,
    )


def _require_openssl() -> str:
    executable = shutil.which(OPENSSL)
    if not executable:
        raise EncryptionError("OpenSSL is required for vault encryption but was not found on PATH")
    return executable


def _openssl_crypt(payload: bytes, key: bytes, iv: bytes, decrypt: bool = False) -> bytes:
    command = [
        _require_openssl(),
        "enc",
        "-aes-256-cbc",
        "-K",
        key.hex(),
        "-iv",
        iv.hex(),
    ]
    if decrypt:
        command.append("-d")
    result = subprocess.run(command, input=payload, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        raise EncryptionError("OpenSSL encryption operation failed")
    return result.stdout


def _mac_payload(aad: dict[str, Any], iv: bytes, ciphertext: bytes) -> bytes:
    return canonical_json(aad) + b"\n" + iv + b"\n" + ciphertext


@dataclass(frozen=True)
class EncryptedEnvelope:
    """JSON-serializable encrypted object envelope."""

    algorithm: str
    kdf: str
    salt: str
    iv: str
    ciphertext: str
    tag: str
    aad: dict[str, Any]
    schema_version: int = ENVELOPE_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "algorithm": self.algorithm,
            "kdf": self.kdf,
            "salt": self.salt,
            "iv": self.iv,
            "ciphertext": self.ciphertext,
            "tag": self.tag,
            "aad": self.aad,
        }

    def to_json_bytes(self) -> bytes:
        return json.dumps(self.to_dict(), sort_keys=True, indent=2).encode("utf-8") + b"\n"

    @classmethod
    def from_json_bytes(cls, payload: bytes) -> "EncryptedEnvelope":
        try:
            value = json.loads(payload.decode("utf-8"))
            return cls(
                schema_version=int(value["schema_version"]),
                algorithm=str(value["algorithm"]),
                kdf=str(value["kdf"]),
                salt=str(value["salt"]),
                iv=str(value["iv"]),
                ciphertext=str(value["ciphertext"]),
                tag=str(value["tag"]),
                aad=dict(value.get("aad", {})),
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise EncryptionError("Invalid encrypted envelope") from exc


def encrypt_payload(plaintext: bytes, passphrase: str, aad: dict[str, Any]) -> bytes:
    """Encrypt bytes into a JSON envelope."""
    salt = os.urandom(SALT_BYTES)
    iv = os.urandom(IV_BYTES)
    key_material = derive_key(passphrase, salt)
    encryption_key = key_material[:32]
    mac_key = key_material[32:]
    ciphertext = _openssl_crypt(plaintext, encryption_key, iv)
    tag = hmac.new(mac_key, _mac_payload(aad, iv, ciphertext), hashlib.sha256).digest()
    envelope = EncryptedEnvelope(
        algorithm=ALGORITHM,
        kdf=KDF,
        salt=_b64encode(salt),
        iv=_b64encode(iv),
        ciphertext=_b64encode(ciphertext),
        tag=_b64encode(tag),
        aad=aad,
    )
    return envelope.to_json_bytes()


def decrypt_payload(envelope_bytes: bytes, passphrase: str, expected_aad: dict[str, Any] | None = None) -> bytes:
    """Decrypt a JSON envelope and optionally require exact associated data."""
    envelope = EncryptedEnvelope.from_json_bytes(envelope_bytes)
    if envelope.schema_version != ENVELOPE_SCHEMA_VERSION:
        raise EncryptionError(f"Unsupported envelope schema version: {envelope.schema_version}")
    if envelope.algorithm != ALGORITHM:
        raise EncryptionError(f"Unsupported encryption algorithm: {envelope.algorithm}")
    if envelope.kdf != KDF:
        raise EncryptionError(f"Unsupported key derivation function: {envelope.kdf}")
    if expected_aad is not None and envelope.aad != expected_aad:
        raise EncryptionError("Encrypted envelope associated data did not match expected metadata")

    try:
        salt = _b64decode(envelope.salt)
        iv = _b64decode(envelope.iv)
        ciphertext = _b64decode(envelope.ciphertext)
        supplied_tag = _b64decode(envelope.tag)
    except ValueError as exc:
        raise EncryptionError("Invalid base64 in encrypted envelope") from exc

    key_material = derive_key(passphrase, salt)
    encryption_key = key_material[:32]
    mac_key = key_material[32:]
    expected_tag = hmac.new(mac_key, _mac_payload(envelope.aad, iv, ciphertext), hashlib.sha256).digest()
    if not hmac.compare_digest(supplied_tag, expected_tag):
        raise EncryptionError("Unable to authenticate payload with the supplied passphrase")
    return _openssl_crypt(ciphertext, encryption_key, iv, decrypt=True)
