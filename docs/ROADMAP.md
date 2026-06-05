# Roadmap, Cost, and Milestones

## Recommended option

Start with the free web app path:

- React/Vite web app for iPhone Safari, Android browsers, desktop browsers, and tablets.
- Cloudflare Worker backend.
- Client-side encryption before upload.
- Optional Firebase identity integration.
- Optional native/Android integrations after the web MVP is validated.

## Milestones

| Milestone | Scope | Status |
| --- | --- | --- |
| Backend API | Session, devices, encrypted data, encrypted backups | Implemented |
| Shared encryption | PBKDF2-SHA256 + AES-GCM JSON envelopes | Implemented |
| Web scaffold | Login, dashboard, bookmarks, settings | Implemented |
| Firebase identity | Email/password sign-in through Firebase | Scaffolded, not wired |
| Vercel deployment | Static web deployment config | Implemented |
| Native apps | iOS/Android deeper browser integration | Future |

## Cost model

The implementation is designed for free-tier friendly hosting:

- Cloudflare Workers for API hosting.
- Vercel or any static host for the web app.
- Firebase only if identity/database features are enabled.

Actual costs depend on provider limits and project traffic. Keep encrypted payload sizes small and store only user-approved sync data.
