# Privacy Sync Free

Privacy Sync Free is an end-to-end encrypted, account-light browser data synchronization system for bookmarks, history, settings, and recovery backups.

The goal is to protect users who rely on Brave/iOS/Android/Desktop browser data from losing their last synced device, while keeping cloud providers unable to read plaintext sync data.

## Recommended architecture

```text
Browser / Web App / Optional Android App
        |
        | encrypts locally
        v
Cloudflare Worker REST API
        |
        | stores opaque encrypted records
        v
Cloudflare Durable Object session storage
```

The web app runs on iPhone Safari, Android Chrome/Brave, desktop browsers, and tablets. It does not require browser extensions for the MVP.

## What is implemented

- Cloudflare Worker backend with session, device, encrypted data, and encrypted backup endpoints.
- React/Vite web app with login, dashboard, bookmarks manager, and settings pages.
- Shared Web Crypto helper for password-derived AES-GCM encrypted backups.
- Frontend local storage sync service for device state, bookmarks, and backup metadata.
- Docs for quick start, deployment, API, architecture, Firebase setup, React guide, testing, roadmap, and cost planning.

## Repository layout

```text
backend/   Cloudflare Worker API
web/       React/Vite app
shared/    Shared client-side crypto utilities
docs/      Planning and setup guides
examples/  JavaScript client example
```

## Quick start

```bash
npm install
npm test
npm run build
```

Run the web app locally:

```bash
npm run dev -w web
```

Run the Worker locally after installing Wrangler:

```bash
npm run dev -w backend
```

## Privacy model

- The backend stores encrypted payloads and metadata only.
- Encryption and decryption happen in the client.
- The user recovery password is never sent to the backend.
- Session IDs and device IDs are random identifiers, not account identities.

## MVP limitations

The web app can manage browser-like bookmarks entered or imported by the user. Mobile operating systems do not allow a normal web app to silently read Brave's private app sandbox. Native app or browser-extension integrations can be added later for deeper automation.
