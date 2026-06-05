"""Storage backends for encrypted vault objects."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from .config import VaultConfig
from .errors import ConfigError, StorageError


class StorageBackend(ABC):
    """Abstract encrypted object storage."""

    @abstractmethod
    def put_bytes(self, key: str, payload: bytes) -> None:
        """Store bytes under a key."""

    @abstractmethod
    def get_bytes(self, key: str) -> bytes:
        """Load bytes for a key."""

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Return whether a key exists."""

    @abstractmethod
    def list_keys(self, prefix: str) -> list[str]:
        """List keys below a prefix."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a key if present."""


class LocalStorageBackend(StorageBackend):
    """Filesystem-backed storage for local development and tests."""

    def __init__(self, root: Path) -> None:
        self.root = root.expanduser()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, key: str) -> Path:
        normalized = key.strip("/")
        path = (self.root / normalized).resolve()
        root = self.root.resolve()
        if root != path and root not in path.parents:
            raise StorageError(f"Storage key escapes local backend root: {key}")
        return path

    def put_bytes(self, key: str, payload: bytes) -> None:
        path = self._path_for(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)

    def get_bytes(self, key: str) -> bytes:
        path = self._path_for(key)
        if not path.exists():
            raise StorageError(f"Object does not exist: {key}")
        return path.read_bytes()

    def exists(self, key: str) -> bool:
        return self._path_for(key).exists()

    def list_keys(self, prefix: str) -> list[str]:
        prefix = prefix.strip("/")
        base = self._path_for(prefix)
        if not base.exists():
            return []
        if base.is_file():
            return [prefix]
        keys: list[str] = []
        for path in base.rglob("*"):
            if path.is_file():
                keys.append(path.relative_to(self.root).as_posix())
        return sorted(keys)

    def delete(self, key: str) -> None:
        path = self._path_for(key)
        if path.exists():
            path.unlink()


class R2StorageBackend(StorageBackend):
    """Cloudflare R2 backend using the S3-compatible API."""

    def __init__(self, config: VaultConfig) -> None:
        if not config.r2_bucket or not config.r2_endpoint_url:
            raise ConfigError("R2_BUCKET and R2_ENDPOINT are required for the r2 backend")
        if not config.r2_access_key_id or not config.r2_secret_access_key:
            raise ConfigError("R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY are required for the r2 backend")
        try:
            import boto3  # type: ignore[import-untyped]
            from botocore.exceptions import ClientError  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ConfigError("Install the R2 extra first: pip install 'brace-sync-last-device[r2]'") from exc

        self._client_error = ClientError
        self.bucket = config.r2_bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=config.r2_endpoint_url,
            aws_access_key_id=config.r2_access_key_id,
            aws_secret_access_key=config.r2_secret_access_key,
            region_name="auto",
        )

    def put_bytes(self, key: str, payload: bytes) -> None:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=payload, ContentType="application/json")

    def get_bytes(self, key: str) -> bytes:
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except self._client_error as exc:  # type: ignore[misc]
            raise StorageError(f"Object does not exist or cannot be read: {key}") from exc

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except self._client_error:  # type: ignore[misc]
            return False

    def list_keys(self, prefix: str) -> list[str]:
        keys: list[str] = []
        token: str | None = None
        while True:
            kwargs = {"Bucket": self.bucket, "Prefix": prefix.strip("/")}
            if token:
                kwargs["ContinuationToken"] = token
            response = self.client.list_objects_v2(**kwargs)
            keys.extend(item["Key"] for item in response.get("Contents", []))
            if not response.get("IsTruncated"):
                return sorted(keys)
            token = response.get("NextContinuationToken")

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)


def build_storage(config: VaultConfig) -> StorageBackend:
    """Create a storage backend from config."""
    if config.backend == "local":
        if not config.local_storage_path:
            raise ConfigError("local_storage_path is required for the local backend")
        return LocalStorageBackend(config.local_storage_path)
    if config.backend == "r2":
        return R2StorageBackend(config)
    raise ConfigError(f"Unsupported storage backend: {config.backend}")
