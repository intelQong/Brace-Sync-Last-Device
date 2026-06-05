# Quickstart

## Prerequisites

- Node.js 18+
- npm
- Cloudflare account for deployment
- Optional: Vercel account for web hosting

## Install and verify

```bash
npm install
npm test
npm run build
```

## Run locally

Terminal 1:

```bash
npm run dev -w backend
```

Terminal 2:

```bash
npm run dev -w web
```

Open the Vite URL, sign in with an email/device name, add bookmarks, create a session, and sync with a recovery password.

## Environment variables

Create `web/.env.local` if your Worker is not on `http://localhost:8787`:

```bash
VITE_API_BASE_URL=https://privacy-sync.example.workers.dev
```

Firebase variables are optional for the current local-first MVP and documented in `FIREBASE-SETUP.md`.
