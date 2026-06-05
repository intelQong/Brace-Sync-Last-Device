# Deployment

## Cloudflare Worker

```bash
cd backend
npm install
npx wrangler login
npm run deploy
```

After deploy, copy the Worker URL.

## Web app on Vercel

Set this environment variable in Vercel:

```bash
VITE_API_BASE_URL=https://privacy-sync.<subdomain>.workers.dev
```

Deploy:

```bash
npm install -g vercel
vercel --prod
```

## Local production build

```bash
npm install
npm run build
```

The static web output is written to `web/dist`.
