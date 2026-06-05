# API Reference

The Cloudflare Worker exposes REST endpoints under `/sync`.

## Session management

### `GET /sync/new`

Creates a session.

Response:

```json
{
  "status": 201,
  "sessionId": "session_...",
  "endpoint": "/sync/session_..."
}
```

### `POST /sync/{sessionId}/register`

Registers or updates a device.

Body:

```json
{
  "deviceId": "device_1",
  "deviceName": "iPhone",
  "publicKey": "public-key-material"
}
```

### `GET /sync/{sessionId}/session`

Returns public session metadata: devices, data types, and backup metadata.

### `DELETE /sync/{sessionId}/session`

Deletes the session and all encrypted records stored in it.

## Data sync

### `PUT /sync/{sessionId}/data/{type}`

Stores encrypted data for a type such as `bookmarks`, `history`, or `settings`.

Body:

```json
{
  "deviceId": "device_1",
  "dataType": "bookmarks",
  "encryptedData": {
    "version": 1,
    "algorithm": "AES-GCM",
    "ciphertext": "base64"
  }
}
```

### `GET /sync/{sessionId}/data/{type}`

Downloads the encrypted payload and upload metadata.

### `GET /sync/{sessionId}/data`

Lists encrypted data types without returning ciphertext.

### `DELETE /sync/{sessionId}/data/{type}`

Deletes one encrypted data type.

## Backups

### `POST /sync/{sessionId}/backup`

Creates a password-encrypted recovery backup.

### `GET /sync/{sessionId}/backup`

Lists backup metadata.

### `GET /sync/{sessionId}/backup/{backupId}`

Downloads one encrypted backup.

### `PUT /sync/{sessionId}/backup/{backupId}`

Updates backup metadata.

### `DELETE /sync/{sessionId}/backup/{backupId}`

Deletes one backup.
