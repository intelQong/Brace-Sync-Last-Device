# React Guide

## Pages

- `Login.jsx`: local sign-in/device bootstrap.
- `Dashboard.jsx`: session creation, device registration, manual encrypted sync, and recovery backup creation.
- `Bookmarks.jsx`: add/delete bookmark records.
- `Settings.jsx`: auto-sync preferences and latest backup information.

## Hooks

- `useAuth`: creates local user and device metadata.
- `useBookmarks`: manages bookmark CRUD in local state.
- `useSync`: encrypts bookmarks/backups and calls the Worker API.
- `useLocalStorageState`: persists client state between browser reloads.

## Encryption flow

1. User enters a recovery password.
2. `encryptJson` derives an AES-GCM key from the password with PBKDF2-SHA256.
3. Bookmark or backup JSON is encrypted locally.
4. The encrypted envelope is uploaded to the Worker.
