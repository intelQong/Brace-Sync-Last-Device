# Brace Sync Last Device

A mobile-first backup design for protecting Brave Browser Sync data when the last device in a Sync Chain is lost.

The project is intentionally **browser-extension-free**. It focuses on encrypted cloud backup and restore workflows using services that can fit a privacy-focused, low-cost setup:

- **Cloudflare R2** for encrypted backup objects.
- **GitHub** for small encrypted manifests, runbooks, and optional automation.
- **Local client-side encryption** so cloud providers never receive plaintext browser data.

## Important mobile constraint

Brave on iOS and Android is much harder to back up directly than Brave Desktop because mobile operating systems sandbox application data. A normal cloud service cannot simply read Brave's private app database from another app without platform-specific permissions, user exports, device backup APIs, root/jailbreak access, or Brave exposing an official export/sync interface.

Because of that, the recommended product direction is not "silently copy Brave mobile profile files." The safer direction is:

1. Keep a minimal always-recoverable Sync Chain record, including setup metadata and user-owned recovery instructions.
2. Use Brave's own Sync Chain as the live sync mechanism.
3. Back up user-accessible exports where available.
4. Use an encrypted recovery vault in Cloudflare R2.
5. Use GitHub only for small encrypted manifests and automation.

## What this can protect

This project should protect against the scenario where:

- The user has Brave Sync enabled on iOS and/or Android.
- The last remaining device in the Brave Sync Chain is lost, wiped, or unavailable.
- The user still has their separate recovery passphrase/key for this backup system.
- The user needs a reliable record of how to recover, rejoin, or reconstruct as much Brave data as the mobile platforms allow.

## What this should not claim

This project should not claim it can fully restore all Brave iOS/Android internal data without Brave support or operating-system backup support.

In particular, the first version should not claim automatic backup of:

- Password databases.
- Cookies and session tokens.
- Internal Brave Sync engine state.
- Private app sandbox files on iOS.
- Private app sandbox files on Android without explicit platform support.

## Proposed MVP

The MVP is a **mobile recovery vault**:

1. A setup wizard helps the user record recovery metadata.
2. The user stores the Brave Sync words/QR-derived setup material only after client-side encryption.
3. Encrypted recovery manifests are uploaded to Cloudflare R2.
4. GitHub stores an encrypted manifest pointer and optional scheduled verification workflow.
5. A restore runbook guides the user through adding a new Brave device to the Sync Chain or rebuilding from exported data.


## Implemented CLI

The first implementation is a Python CLI named `brace-sync`. It creates an encrypted recovery vault, stores user-provided Brave Sync recovery material or export files, and verifies that encrypted objects can be decrypted later.

### Run from a source checkout

The core CLI has no mandatory third-party Python package dependency. It requires Python 3.11+ and the system `openssl` command.

```bash
./bin/brace-sync --help
```

Install the optional R2 dependency only when using Cloudflare R2 directly from the CLI:

```bash
pip install boto3
```

### Quick start with local storage

```bash
export BRACE_SYNC_PASSPHRASE='use-a-long-private-recovery-passphrase'
./bin/brace-sync --config ./vault-config.json init-vault --backend local --local-storage ./vault-objects
printf 'brave sync recovery material' | ./bin/brace-sync --config ./vault-config.json save-sync-recovery
./bin/brace-sync --config ./vault-config.json list-snapshots
./bin/brace-sync --config ./vault-config.json verify-vault
./bin/brace-sync restore-guide --platform android
```

### Cloudflare R2 configuration

The R2 backend uses Cloudflare's S3-compatible API. Configure credentials with environment variables instead of committing secrets:

```bash
export R2_BUCKET='your-bucket'
export R2_ENDPOINT='https://<account-id>.r2.cloudflarestorage.com'
export R2_ACCESS_KEY_ID='...'
export R2_SECRET_ACCESS_KEY='...'
export BRACE_SYNC_PASSPHRASE='use-a-long-private-recovery-passphrase'
./bin/brace-sync init-vault --backend r2
```

The vault encryption passphrase is separate from GitHub and Cloudflare credentials. Losing the passphrase makes encrypted recovery objects unrecoverable.

## Repository status

This repository currently contains the planning documents for the mobile-first architecture. Implementation should begin after choosing the client type:

- Native Android app.
- Native iOS app.
- Desktop companion app.
- Command-line tool for recovery vault management.
- Cloudflare Worker API for signed upload/download URLs.

See [`docs/mobile-architecture.md`](docs/mobile-architecture.md) for the recommended architecture.
