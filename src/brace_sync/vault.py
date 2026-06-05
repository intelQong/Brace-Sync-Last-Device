"""High-level recovery vault operations."""

from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path

from .config import VaultConfig
from .crypto import decrypt_payload, encrypt_payload
from .errors import StorageError
from .models import Manifest, VaultObject, utc_now_iso
from .storage import StorageBackend

MANIFEST_AAD_TYPE = "manifest"


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


class RecoveryVault:
    """Encrypted recovery vault facade."""

    def __init__(self, config: VaultConfig, storage: StorageBackend) -> None:
        self.config = config
        self.storage = storage

    def new_manifest(self) -> Manifest:
        now = utc_now_iso()
        return Manifest(vault_id=self.config.vault_id, created_at=now, updated_at=now, objects=[])

    def load_manifest(self, passphrase: str) -> Manifest:
        if not self.storage.exists(self.config.manifest_key):
            return self.new_manifest()
        encrypted = self.storage.get_bytes(self.config.manifest_key)
        plaintext = decrypt_payload(encrypted, passphrase, self._manifest_aad())
        return Manifest.from_dict(json.loads(plaintext.decode("utf-8")))

    def save_manifest(self, manifest: Manifest, passphrase: str) -> None:
        manifest.updated_at = utc_now_iso()
        plaintext = json.dumps(manifest.to_dict(), sort_keys=True, indent=2).encode("utf-8") + b"\n"
        encrypted = encrypt_payload(plaintext, passphrase, self._manifest_aad())
        self.storage.put_bytes(self.config.manifest_key, encrypted)

    def add_bytes(self, object_type: str, payload: bytes, passphrase: str, description: str = "") -> VaultObject:
        manifest = self.load_manifest(passphrase)
        object_id = uuid.uuid4().hex
        created_at = utc_now_iso()
        storage_key = self.config.object_key(object_id)
        aad = self._object_aad(object_id=object_id, object_type=object_type, created_at=created_at)
        encrypted = encrypt_payload(payload, passphrase, aad)
        self.storage.put_bytes(storage_key, encrypted)
        metadata = VaultObject(
            object_id=object_id,
            object_type=object_type,
            storage_key=storage_key,
            sha256=_sha256(payload),
            size=len(payload),
            created_at=created_at,
            description=description,
        )
        manifest.objects.append(metadata)
        self.save_manifest(manifest, passphrase)
        return metadata

    def add_file(self, path: Path, passphrase: str, object_type: str = "user-export", description: str = "") -> VaultObject:
        if not path.exists() or not path.is_file():
            raise StorageError(f"Export file does not exist: {path}")
        return self.add_bytes(object_type, path.read_bytes(), passphrase, description or path.name)

    def read_object(self, object_id: str, passphrase: str) -> bytes:
        manifest = self.load_manifest(passphrase)
        metadata = self.find_object(manifest, object_id)
        encrypted = self.storage.get_bytes(metadata.storage_key)
        plaintext = decrypt_payload(
            encrypted,
            passphrase,
            self._object_aad(
                object_id=metadata.object_id,
                object_type=metadata.object_type,
                created_at=metadata.created_at,
            ),
        )
        if _sha256(plaintext) != metadata.sha256:
            raise StorageError(f"Checksum mismatch for object: {object_id}")
        return plaintext

    def verify(self, passphrase: str) -> tuple[Manifest, list[VaultObject]]:
        manifest = self.load_manifest(passphrase)
        verified: list[VaultObject] = []
        for metadata in manifest.objects:
            self.read_object(metadata.object_id, passphrase)
            verified.append(metadata)
        return manifest, verified

    @staticmethod
    def find_object(manifest: Manifest, object_id: str) -> VaultObject:
        for metadata in manifest.objects:
            if metadata.object_id == object_id:
                return metadata
        raise StorageError(f"Object not found in manifest: {object_id}")

    def _manifest_aad(self) -> dict[str, str]:
        return {"object_type": MANIFEST_AAD_TYPE, "vault_id": self.config.vault_id}

    def _object_aad(self, object_id: str, object_type: str, created_at: str) -> dict[str, str]:
        return {
            "object_id": object_id,
            "object_type": object_type,
            "created_at": created_at,
            "vault_id": self.config.vault_id,
        }
