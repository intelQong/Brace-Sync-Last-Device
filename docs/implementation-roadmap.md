# Implementation roadmap

## Phase 1: recovery vault CLI

Build a command-line tool first because it is simpler to audit and can run on a desktop or development machine.

Commands:

- `init-vault`: create local configuration and recovery key material.
- `save-sync-recovery`: encrypt and store Brave Sync recovery material supplied by the user.
- `save-export`: encrypt and store a user-provided Brave export file.
- `list-snapshots`: list encrypted vault snapshots from Cloudflare R2.
- `verify-vault`: download and decrypt the latest vault object to confirm recoverability.
- `restore-guide`: print platform-specific restore instructions.

## Phase 2: Cloudflare R2 backend

Implement S3-compatible object storage for encrypted objects.

Configuration:

- `R2_ACCOUNT_ID`
- `R2_BUCKET`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_ENDPOINT`

Rules:

- The storage backend must reject plaintext payloads.
- Object names must avoid leaking sensitive user/device details.
- Retention must keep multiple snapshots so accidental overwrite does not destroy recovery data.

## Phase 3: GitHub manifest and automation

Add GitHub integration only for small metadata.

Recommended files:

- `.github/workflows/verify-vault.yml`
- `manifests/vault-pointer.enc`

Automation should:

- Check that expected R2 objects exist.
- Report stale backups.
- Avoid downloading or decrypting user secrets inside GitHub Actions unless the user explicitly chooses that model.

## Phase 4: mobile app

After the CLI works, build a native mobile app focused on recovery UX.

Mobile app screens:

- Vault setup.
- Recovery key confirmation.
- Brave Sync recovery material capture.
- Export upload/import guidance.
- Backup health.
- Restore guide.

The mobile app should not promise to read Brave's private app sandbox.

## Phase 5: optional desktop companion

Add a desktop companion for users who also run Brave on Windows, macOS, or Linux.

The desktop companion can support richer profile backup because desktop profile directories are accessible to the user account. It should still encrypt everything before upload.

## Current implementation status

Implemented in this repository:

- Python package scaffold with the `brace-sync` console command.
- Local encrypted object storage backend for development and tests.
- Optional Cloudflare R2 backend through the `r2` Python extra.
- AES-256-CBC with HMAC-SHA256 encrypted envelopes with scrypt-derived keys.
- Encrypted manifest creation and loading.
- `init-vault`, `save-sync-recovery`, `save-export`, `list-snapshots`, `verify-vault`, `restore-object`, and `restore-guide` commands.
- Unit tests for encryption and vault round-trips.

Still pending:

- Native iOS app.
- Native Android app.
- Cloudflare Worker signed URL broker.
- GitHub Actions health-check workflow.
