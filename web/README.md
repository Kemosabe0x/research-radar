# RSSAgent UI

Initial Next.js + shadcn-style dashboard for:

- latest ingested feed items (`/api/articles`)
- digestion trigger action per item (`POST /api/articles/digest`)
- generated markdown browser (`/api/generated/articles`, `/api/generated/digests`)

## Local dev

1. Start Python API:
   - `uv run rssagent-api --host 127.0.0.1 --port 8787`
2. Start UI:
   - `cd web`
   - `npm install`
   - `npm run dev`

Set `NEXT_PUBLIC_RSSAGENT_API_BASE_URL` if API host/port differs.
