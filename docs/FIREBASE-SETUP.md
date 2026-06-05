# Firebase Setup

Firebase is optional for the current Worker-first MVP. Use it when you want email/password identity, hosted user profiles, or Realtime Database mirroring.

## Create project

1. Open Firebase Console.
2. Create a project named `privacy-sync`.
3. Enable Authentication with Email/Password.
4. Enable Realtime Database or Firestore.

## Web environment variables

Add these to `web/.env.local` or your Vercel environment:

```bash
VITE_FIREBASE_API_KEY=...
VITE_FIREBASE_AUTH_DOMAIN=...
VITE_FIREBASE_DATABASE_URL=...
VITE_FIREBASE_PROJECT_ID=...
VITE_FIREBASE_STORAGE_BUCKET=...
VITE_FIREBASE_MESSAGING_SENDER_ID=...
VITE_FIREBASE_APP_ID=...
```

The app exposes a config helper in `web/src/services/firebase.js`; Firebase auth wiring can be added without changing the encrypted sync API.
