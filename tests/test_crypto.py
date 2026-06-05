import pytest

from brace_sync.crypto import decrypt_payload, encrypt_payload
from brace_sync.errors import EncryptionError


def test_encrypt_decrypt_round_trip():
    aad = {"object_type": "test", "vault_id": "vault"}
    encrypted = encrypt_payload(b"secret brave sync material", "passphrase", aad)

    assert b"secret brave sync material" not in encrypted
    assert decrypt_payload(encrypted, "passphrase", aad) == b"secret brave sync material"


def test_decrypt_rejects_wrong_passphrase():
    aad = {"object_type": "test", "vault_id": "vault"}
    encrypted = encrypt_payload(b"secret", "correct", aad)

    with pytest.raises(EncryptionError):
        decrypt_payload(encrypted, "wrong", aad)


def test_decrypt_rejects_wrong_aad():
    encrypted = encrypt_payload(b"secret", "passphrase", {"object_type": "test"})

    with pytest.raises(EncryptionError):
        decrypt_payload(encrypted, "passphrase", {"object_type": "other"})
