# Testing

Run all current automated tests:

```bash
npm test
```

Run package checks individually:

```bash
npm run test -w backend
npm run test -w shared
npm run lint -w backend
npm run lint -w shared
```

Run a web production build after dependencies are installed:

```bash
npm run build -w web
```

## Manual smoke test

1. Start the Worker with `npm run dev -w backend`.
2. Start the web app with `npm run dev -w web`.
3. Sign in with any email and device name.
4. Add a bookmark.
5. Create a session.
6. Sync bookmarks with a recovery password.
7. Create a recovery backup.
