"""Domain-specific exceptions for the recovery vault."""


class BraceSyncError(Exception):
    """Base error for expected CLI failures."""


class ConfigError(BraceSyncError):
    """Raised when configuration is missing or invalid."""


class StorageError(BraceSyncError):
    """Raised when storage operations fail."""


class EncryptionError(BraceSyncError):
    """Raised when encryption or decryption fails."""
