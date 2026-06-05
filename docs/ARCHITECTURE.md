# Architecture

Privacy Sync Free uses a web-first implementation so iPhone, Android, desktop, and tablet users can start without app-store distribution.

## Components

```text
web/ React app
  ├─ local device state
  ├─ bookmark manager
  ├─ recovery password prompt
  └─ Web Crypto encryption

backend/ Cloudflare Worker
  ├─ REST API
  ├─ Durable Object session storage
  └─ encrypted payload persistence

shared/ crypto helpers
  ├─ PBKDF2-SHA256
  ├─ AES-GCM
  └─ JSON encrypted envelopes
```

## Security model

- The recovery password is entered on the client only.
- The client encrypts JSON payloads before upload.
- The Worker validates routing and metadata but cannot decrypt payloads.
- The Worker stores `encryptedData` and `encryptedBackup` as opaque JSON.
- Session IDs, device IDs, and backup IDs are random.

## Mobile browser reality

A web app cannot silently read Brave's private app data on iOS or Android. The MVP manages user-entered/imported bookmark data and recovery backups. Deeper automatic Brave integration requires a native app, OS-supported import/export, or extension support on platforms that allow it.
