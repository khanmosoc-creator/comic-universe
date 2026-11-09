# Deployment — Cloudflare Workers Static Assets (free)

> **Live URL:** <https://super-zayds-maze-guardians.khanmosoc.workers.dev>

## How it works

The repo root contains `wrangler.jsonc`, which tells Cloudflare's Git integration to deploy `apps/web/dist`
as a Workers Static Assets site with SPA fallback. Every push to `main` triggers an automatic build and
deploy; every pull request gets its own preview URL.

### Build settings (configured in Cloudflare dashboard)

| Setting | Value |
| --- | --- |
| Project name | `super-zayds-maze-guardians` |
| Production branch | `main` |
| Build command | `cd apps/web && npm ci && npm run build` |
| Build output directory | `apps/web/dist` |
| Root directory | *(empty = repo root)* |
| Env var | `NODE_VERSION=22` (optional; `.node-version` pins 22) |

Web Analytics is **disabled**.

## Routing

`wrangler.jsonc` sets `"not_found_handling": "single-page-application"`, so any path that isn't a real
file returns `index.html` — direct loads and refreshes of `/heroes/zayd`, `/read/issue-1?panel=5` etc.
work, while real files (`/assets/*`, `/art/*`, `/fonts/*`) are served as-is. Unknown paths render the
in-app "Wrong turn" page (HTTP 200, a known SPA trade-off).

## Headers

`apps/web/public/_headers` sets a strict CSP and other security headers on every response and long-lived
caching on hashed `/assets/*`.

## Verify after each deploy

```bash
python3 apps/web/scripts/e2e_check.py https://super-zayds-maze-guardians.khanmosoc.workers.dev /tmp/shots
curl -sI https://super-zayds-maze-guardians.khanmosoc.workers.dev/heroes/zayd | grep -iE "HTTP/|content-security-policy"
```

## Custom domain later (commercial launch)

Workers & Pages project → **Custom domains** → add the domain (DNS on Cloudflare is easiest). The
`.workers.dev` URL keeps working. Re-check the zone settings listed in `privacy-compliance-checklist.md` § B.

## Cost (Free plan)

$0. Static asset requests and bandwidth are free on the Workers Free plan; limits that matter: 500
builds/month, one concurrent build, 20-minute build timeout, 20,000 files per site, 25 MiB per file, 100
custom domains per project. This site is about 70 files (~2 MB) and builds in roughly a minute. GitHub
Actions minutes are free for public repositories.

## Fallback: manual deploy without Git

```bash
cd apps/web && npm ci && npm run build
cd ../..
npx wrangler deploy
```
