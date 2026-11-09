# Deployment — Cloudflare Pages (free)

## One-time setup (Git integration)

1. Cloudflare dashboard → **Workers & Pages** → **Create** → Pages → **Import an existing Git repository**.
2. Connect GitHub and grant the Cloudflare Pages app access to **`comic-universe`** only.
3. Build settings:

| Setting | Value |
| --- | --- |
| Project name | `super-zayds-maze-guardians` → `https://super-zayds-maze-guardians.pages.dev` (Cloudflare adds a suffix if taken) |
| Production branch | `main` |
| Framework preset | None |
| Build command | `cd apps/web && npm ci && npm run build` |
| Build output directory | `apps/web/dist` |
| Root directory | *(empty = repo root)* |
| Env var | `NODE_VERSION=22` (optional; `.node-version` pins 22) |

4. **Save and Deploy.** Leave Web Analytics **disabled**.

Every push to `main` deploys production; every pull request gets its own preview URL.

## Routing

The build has **no `404.html`**, so Pages runs in single-page-app mode and returns `index.html` for any path
that isn't a file — direct loads and refreshes of `/heroes/zayd`, `/read/issue-1?panel=5` etc. work, while
real files (`/assets/*`, `/art/*`, `/fonts/*`) are served as-is. Do **not** add a `/* /index.html 200`
`_redirects` rule. Unknown paths render the in-app "Wrong turn" page (HTTP 200, a known SPA trade-off).

## Headers

`apps/web/public/_headers` sets a strict CSP and other security headers on every response and long-lived
caching on hashed `/assets/*`.

## Verify after each deploy

```bash
python3 apps/web/scripts/e2e_check.py https://super-zayds-maze-guardians.pages.dev /tmp/shots
curl -sI https://super-zayds-maze-guardians.pages.dev/heroes/zayd | grep -iE "HTTP/|content-security-policy"
```

## Custom domain later (commercial launch)

Pages project → **Custom domains** → add the domain (DNS on Cloudflare is easiest). The `.pages.dev` URL
keeps working. Re-check the zone settings listed in `privacy-compliance-checklist.md` § B.

## Cost (Free plan)

$0. Static asset requests and bandwidth on Pages are free; limits that matter: 500 builds/month, one
concurrent build, 20-minute build timeout, 20,000 files per site, 25 MiB per file, 100 custom domains per
project. This site uses ~70 files (~2 MB) and builds in about a minute.

## Fallback: manual upload without Git

```bash
cd apps/web && npm ci && npm run build
npx wrangler pages deploy dist --project-name super-zayds-maze-guardians --branch main
```
