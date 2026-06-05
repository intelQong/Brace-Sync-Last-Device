"""Vault configuration loading and persistence."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ConfigError
from .models import utc_now_iso

CONFIG_SCHEMA_VERSION = 1
DEFAULT_CONFIG_DIR = Path.home() / ".config" / "brace-sync"
DEFAULT_OBJECT_PREFIX = "vaults"


@dataclass(frozen=True)
class VaultConfig:
    """Local non-secret vault configuration."""

    vault_id: str
    backend: str
    object_prefix: str
    config_path: Path
    local_storage_path: Path | None = None
    r2_bucket: str | None = None
    r2_endpoint_url: str | None = None
    r2_access_key_id: str | None = None
    r2_secret_access_key: str | None = None

    @property
    def manifest_key(self) -> str:
        return f"{self.object_prefix.rstrip('/')}/{self.vault_id}/manifest.enc.json"

    def object_key(self, object_id: str) -> str:
        return f"{self.object_prefix.rstrip('/')}/{self.vault_id}/objects/{object_id}.enc.json"

    def redacted_dict(self) -> dict[str, Any]:
        value = {
            "schema_version": CONFIG_SCHEMA_VERSION,
            "vault_id": self.vault_id,
            "backend": self.backend,
            "object_prefix": self.object_prefix,
            "local_storage_path": str(self.local_storage_path) if self.local_storage_path else None,
            "r2_bucket": self.r2_bucket,
            "r2_endpoint_url": self.r2_endpoint_url,
            "r2_access_key_id": self.r2_access_key_id,
            "r2_secret_access_key": "***" if self.r2_secret_access_key else None,
        }
        return {key: item for key, item in value.items() if item is not None}


def default_config_path() -> Path:
    return Path(os.environ.get("BRACE_SYNC_CONFIG", DEFAULT_CONFIG_DIR / "config.json")).expanduser()


def create_default_config(config_path: Path, backend: str, local_storage_path: Path | None = None) -> VaultConfig:
    vault_id = uuid.uuid4().hex
    object_prefix = os.environ.get("BRACE_SYNC_OBJECT_PREFIX", DEFAULT_OBJECT_PREFIX)
    if backend == "local":
        local_storage_path = local_storage_path or config_path.parent / "objects"
    return VaultConfig(
        vault_id=vault_id,
        backend=backend,
        object_prefix=object_prefix,
        config_path=config_path,
        local_storage_path=local_storage_path,
        r2_bucket=os.environ.get("R2_BUCKET"),
        r2_endpoint_url=os.environ.get("R2_ENDPOINT"),
        r2_access_key_id=os.environ.get("R2_ACCESS_KEY_ID"),
        r2_secret_access_key=os.environ.get("R2_SECRET_ACCESS_KEY"),
    )


def save_config(config: VaultConfig) -> None:
    config.config_path.parent.mkdir(parents=True, exist_ok=True)
    payload = config.redacted_dict()
    payload["created_at"] = utc_now_iso()
    payload.pop("r2_secret_access_key", None)
    config.config_path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    try:
        config.config_path.chmod(0o600)
    except OSError:
        pass


def load_config(config_path: Path | None = None) -> VaultConfig:
    path = (config_path or default_config_path()).expanduser()
    if not path.exists():
        raise ConfigError(f"Config file does not exist: {path}. Run init-vault first.")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Config file is not valid JSON: {path}") from exc

    backend = str(value.get("backend", "local"))
    local_storage = value.get("local_storage_path")
    return VaultConfig(
        vault_id=str(value["vault_id"]),
        backend=backend,
        object_prefix=str(value.get("object_prefix", DEFAULT_OBJECT_PREFIX)),
        config_path=path,
        local_storage_path=Path(local_storage).expanduser() if local_storage else None,
        r2_bucket=os.environ.get("R2_BUCKET", value.get("r2_bucket")),
        r2_endpoint_url=os.environ.get("R2_ENDPOINT", value.get("r2_endpoint_url")),
        r2_access_key_id=os.environ.get("R2_ACCESS_KEY_ID", value.get("r2_access_key_id")),
        r2_secret_access_key=os.environ.get("R2_SECRET_ACCESS_KEY"),
    )
