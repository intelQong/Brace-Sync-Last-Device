"""Serializable data models used by the vault."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    """Return a stable UTC timestamp string."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class VaultObject:
    """Metadata for one encrypted vault object."""

    object_id: str
    object_type: str
    storage_key: str
    sha256: str
    size: int
    created_at: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "type": self.object_type,
            "storage_key": self.storage_key,
            "sha256": self.sha256,
            "size": self.size,
            "created_at": self.created_at,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "VaultObject":
        return cls(
            object_id=str(value["object_id"]),
            object_type=str(value["type"]),
            storage_key=str(value["storage_key"]),
            sha256=str(value["sha256"]),
            size=int(value["size"]),
            created_at=str(value["created_at"]),
            description=str(value.get("description", "")),
        )


@dataclass
class Manifest:
    """Encrypted vault manifest payload."""

    vault_id: str
    created_at: str
    updated_at: str
    objects: list[VaultObject] = field(default_factory=list)
    schema_version: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "vault_id": self.vault_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "objects": [obj.to_dict() for obj in self.objects],
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Manifest":
        return cls(
            schema_version=int(value.get("schema_version", 1)),
            vault_id=str(value["vault_id"]),
            created_at=str(value["created_at"]),
            updated_at=str(value["updated_at"]),
            objects=[VaultObject.from_dict(item) for item in value.get("objects", [])],
        )
