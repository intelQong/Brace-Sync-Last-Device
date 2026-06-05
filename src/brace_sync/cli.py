"""Command-line interface for the Brave recovery vault."""

from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path

from .config import create_default_config, default_config_path, load_config, save_config
from .errors import BraceSyncError
from .storage import build_storage
from .vault import RecoveryVault

SYNC_RECOVERY_WARNING = "Store only after confirming nobody else can see your screen or shell history."


def _passphrase(args: argparse.Namespace, *, confirm: bool = False) -> str:
    value = getattr(args, "passphrase", None) or os.environ.get("BRACE_SYNC_PASSPHRASE")
    if value:
        return value
    first = getpass.getpass("Vault passphrase: ")
    if confirm:
        second = getpass.getpass("Confirm vault passphrase: ")
        if first != second:
            raise BraceSyncError("Passphrases did not match")
    return first


def _vault(args: argparse.Namespace) -> RecoveryVault:
    config = load_config(args.config)
    return RecoveryVault(config, build_storage(config))


def init_vault(args: argparse.Namespace) -> int:
    path = (args.config or default_config_path()).expanduser()
    if path.exists() and not args.force:
        raise BraceSyncError(f"Config already exists: {path}. Use --force to replace it.")
    config = create_default_config(path, args.backend, args.local_storage)
    save_config(config)
    vault = RecoveryVault(config, build_storage(config))
    passphrase = _passphrase(args, confirm=True)
    manifest = vault.new_manifest()
    vault.save_manifest(manifest, passphrase)
    print(f"Initialized vault {config.vault_id}")
    print(f"Config: {config.config_path}")
    print(f"Backend: {config.backend}")
    print("Save your vault passphrase separately. Losing it makes recovery impossible.")
    return 0


def save_sync_recovery(args: argparse.Namespace) -> int:
    if args.value and args.file:
        raise BraceSyncError("Use either --value or --file, not both")
    if args.value:
        payload = args.value.encode("utf-8")
    elif args.file:
        payload = args.file.read_bytes()
    else:
        print(SYNC_RECOVERY_WARNING, file=sys.stderr)
        payload = sys.stdin.buffer.read()
    if not payload:
        raise BraceSyncError("No sync recovery material was provided")
    metadata = _vault(args).add_bytes(
        "sync-recovery-record",
        payload,
        _passphrase(args),
        args.description or "Brave Sync recovery material",
    )
    print(f"Stored encrypted sync recovery record: {metadata.object_id}")
    return 0


def save_export(args: argparse.Namespace) -> int:
    metadata = _vault(args).add_file(
        args.file,
        _passphrase(args),
        object_type=args.type,
        description=args.description or args.file.name,
    )
    print(f"Stored encrypted export: {metadata.object_id}")
    return 0


def list_snapshots(args: argparse.Namespace) -> int:
    manifest = _vault(args).load_manifest(_passphrase(args))
    if not manifest.objects:
        print("No encrypted recovery objects found.")
        return 0
    for item in manifest.objects:
        print(f"{item.object_id}\t{item.object_type}\t{item.created_at}\t{item.size} bytes\t{item.description}")
    return 0


def verify_vault(args: argparse.Namespace) -> int:
    manifest, verified = _vault(args).verify(_passphrase(args))
    print(f"Verified manifest for vault {manifest.vault_id}")
    print(f"Verified encrypted objects: {len(verified)}")
    for item in verified:
        print(f"- {item.object_id} {item.object_type} {item.sha256}")
    return 0


def restore_object(args: argparse.Namespace) -> int:
    payload = _vault(args).read_object(args.object_id, _passphrase(args))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(payload)
        print(f"Restored object to {args.output}")
    else:
        sys.stdout.buffer.write(payload)
    return 0


def restore_guide(args: argparse.Namespace) -> int:
    platform = args.platform
    print("Brave mobile last-device restore guide")
    print("======================================")
    print("1. Install Brave on the replacement iOS or Android device.")
    print("2. Open this vault with your separate vault passphrase.")
    print("3. Run `brace-sync list-snapshots` and identify the latest sync-recovery-record.")
    print("4. Run `brace-sync restore-object <object-id> --output recovery.txt` on a private device.")
    print("5. In Brave, use the recovered Sync Chain material to add the replacement device if Brave accepts it.")
    print("6. Import any user export files that you previously saved in this vault.")
    print("7. Run `brace-sync verify-vault` again after updating the vault with the replacement device notes.")
    if platform == "ios":
        print("\niOS note: this tool does not read Brave's private app sandbox. Use Brave-supported recovery or exports.")
    elif platform == "android":
        print("\nAndroid note: this tool does not require root and does not read Brave's private app sandbox.")
    else:
        print("\nMobile note: normal iOS/Android sandboxing prevents direct Brave app-data scraping.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="brace-sync", description="Encrypted Brave Sync last-device recovery vault")
    parser.add_argument("--config", type=Path, help="Path to local vault config JSON")
    parser.add_argument("--passphrase", help="Vault passphrase. Prefer BRACE_SYNC_PASSPHRASE or interactive entry.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init-vault", help="Create a new encrypted recovery vault")
    init.add_argument("--backend", choices=["local", "r2"], default="local")
    init.add_argument("--local-storage", type=Path, help="Local object storage path for development/testing")
    init.add_argument("--force", action="store_true", help="Replace an existing config file")
    init.set_defaults(func=init_vault)

    sync = subparsers.add_parser("save-sync-recovery", help="Encrypt and store Brave Sync recovery material")
    sync.add_argument("--value", help="Recovery material string. Avoid this on shared shells.")
    sync.add_argument("--file", type=Path, help="File containing recovery material")
    sync.add_argument("--description", help="Human-readable encrypted object description")
    sync.set_defaults(func=save_sync_recovery)

    export = subparsers.add_parser("save-export", help="Encrypt and store a user-provided Brave export")
    export.add_argument("file", type=Path)
    export.add_argument("--type", default="user-export", help="Object type label")
    export.add_argument("--description", help="Human-readable encrypted object description")
    export.set_defaults(func=save_export)

    snapshots = subparsers.add_parser("list-snapshots", help="List encrypted objects in the manifest")
    snapshots.set_defaults(func=list_snapshots)

    verify = subparsers.add_parser("verify-vault", help="Decrypt and checksum-verify all vault objects")
    verify.set_defaults(func=verify_vault)

    restore = subparsers.add_parser("restore-object", help="Decrypt one vault object")
    restore.add_argument("object_id")
    restore.add_argument("--output", type=Path, help="Write decrypted payload to a file instead of stdout")
    restore.set_defaults(func=restore_object)

    guide = subparsers.add_parser("restore-guide", help="Print mobile restore instructions")
    guide.add_argument("--platform", choices=["ios", "android", "mobile"], default="mobile")
    guide.set_defaults(func=restore_guide)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except BraceSyncError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
