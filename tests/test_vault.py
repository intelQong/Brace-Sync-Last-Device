from pathlib import Path

from brace_sync.config import create_default_config, save_config
from brace_sync.storage import build_storage
from brace_sync.vault import RecoveryVault


def make_vault(tmp_path: Path) -> RecoveryVault:
    config = create_default_config(tmp_path / "config.json", "local", tmp_path / "objects")
    save_config(config)
    return RecoveryVault(config, build_storage(config))


def test_vault_add_list_verify_and_restore(tmp_path):
    vault = make_vault(tmp_path)
    manifest = vault.new_manifest()
    vault.save_manifest(manifest, "passphrase")

    metadata = vault.add_bytes("sync-recovery-record", b"sync words", "passphrase", "phone")
    loaded = vault.load_manifest("passphrase")

    assert loaded.vault_id == vault.config.vault_id
    assert [item.object_id for item in loaded.objects] == [metadata.object_id]
    assert vault.read_object(metadata.object_id, "passphrase") == b"sync words"

    verified_manifest, verified = vault.verify("passphrase")
    assert verified_manifest.vault_id == vault.config.vault_id
    assert verified == [metadata]


def test_vault_add_file(tmp_path):
    vault = make_vault(tmp_path)
    vault.save_manifest(vault.new_manifest(), "passphrase")
    export = tmp_path / "bookmarks.html"
    export.write_text("<html>bookmarks</html>", encoding="utf-8")

    metadata = vault.add_file(export, "passphrase")

    assert metadata.object_type == "user-export"
    assert vault.read_object(metadata.object_id, "passphrase") == b"<html>bookmarks</html>"
