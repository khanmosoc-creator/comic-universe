# Pre-launch privacy & compliance checklist

Status as of 2026-11-09 for the static MVP. This is an engineering review, **not legal advice**, and it
does not guarantee compliance with any law. Items marked **OWNER/LEGAL** need a decision by the owner or a
qualified lawyer.

## A. Data the site collects — design verification

| Check | Result | How verified |
| --- | --- | --- |
| No accounts, logins, registration, profiles | ✅ None exist | Code review; no auth code or routes |
| No forms, comments, chat, uploads, newsletter | ✅ None exist | No `<form>`/`<input>` in source; CSP `form-action 'none'` |
| No analytics, pixels, tag managers, SDKs | ✅ None | CI fails the build if any external URL appears in HTML/JS/CSS (only the privacy-policy link to cloudflare.com is allowed) |
| No ads or behavioural profiling | ✅ None | Code review |
| No cookies set by the site; no local/session storage | ✅ | E2E test: `document.cookie` empty, `localStorage`/`sessionStorage` length 0 |
| No third-party requests from the reader's browser | ✅ | E2E test records every request; all first-party. CSP `default-src 'self'` blocks anything else |
| Fonts and images self-hosted | ✅ | Poppins WOFF in `/fonts`, all art in `/art` |
| No reader-facing AI generation or external AI API calls | ✅ | Art is generated offline by owner-run scripts |
| No consent banners or age gates | ✅ Not needed while nothing is collected | Re-evaluate before adding any feature in section F |
| Image metadata stripped (EXIF/location) | ✅ | `process_owner_art.py` writes images with no metadata; PIL check shows empty info |

## B. Hosting data processing (Cloudflare Pages)

Removing forms does **not** remove all processing. When a device requests a page, Cloudflare receives the
standard technical data of any HTTP request — IP address, User-Agent, requested URL, Referer (from other
sites linking in), TLS details and timestamps — to deliver, cache and protect the site (DDoS mitigation,
abuse prevention). Cloudflare may keep this in its own logs and may set strictly-necessary security
cookies (e.g. a challenge-clearance cookie) if traffic looks suspicious. The site owner does not receive or
use this data.

Dashboard settings to confirm (**OWNER**, takes 2 minutes):

- [ ] Workers & Pages → *comic-universe* → **Metrics**: Web Analytics is **not enabled** (leave "Enable" unclicked).
- [ ] No Pages Functions are deployed (the repo has no `functions/` directory) — no server code runs.
- [ ] Preview deployments are public by design (anyone with the preview URL). Optional: restrict previews
      with Cloudflare Access.
- [ ] When a custom domain is added later, keep zone features that inject scripts **off**: Web Analytics/RUM
      automatic setup, Zaraz, Rocket Loader, Email Address Obfuscation. (The site's CSP would block injected
      scripts anyway, which would also show console errors.)
- [ ] **OWNER/LEGAL:** review Cloudflare's Privacy Policy and Data Processing Addendum and keep a copy with
      the business records.

The `/privacy` page discloses this hosting processing in plain language and links to Cloudflare's policy.

## C. Children's privacy (COPPA and FTC)

- The site is **directed to children**, so COPPA applies if it collects personal information from children
  under 13. "Personal information" includes persistent identifiers such as IP addresses.
- The only identifiers involved are those processed by the host to deliver and secure the site. The COPPA
  Rule allows persistent identifiers collected **solely to support internal operations** (e.g. serving
  content, security, maintaining the site) without parental consent, provided no other personal
  information is collected and they are not used to contact a specific person, build profiles or target
  advertising. The privacy page states the purpose and that the data is not used to identify, profile or
  contact readers.
- The amended COPPA Rule took effect **June 23, 2025** with a general compliance date of **April 22, 2026**
  (Federal Register, 90 FR, 2025-05904). It revises notice requirements and adds written
  information-security and data-retention obligations for operators that collect children's personal
  information.
- [ ] **OWNER/LEGAL:** confirm the internal-operations reliance and the wording of the online notice
      under the amended Rule; decide whether a written data-retention/security policy is appropriate now.
- [ ] **OWNER:** add a real business contact (postal address and/or email) to `/privacy` — COPPA online
      notices are expected to identify the operator. None was invented.

## D. US state laws

Several states have children's privacy or age-appropriate-design laws with different scopes and
thresholds; most turn on collecting or processing personal data beyond what is strictly necessary, on
profiling/targeted ads, or on social features (profiles, messaging, user posts) — none of which the site has.
- [ ] **OWNER/LEGAL:** confirm no state law obligations are triggered before commercial launch, especially
      if revenue thresholds may be met or if any feature in section F is added.

## E. Copyright, trademarks and consumer protection

- [x] All characters, story and art are original or owner-supplied; generic genre elements only
      (see `ASSET-PROVENANCE.md`). Fonts under OFL with licence shipped.
- [ ] **OWNER:** confirm rights in the five sketches and, if a child drew them, guardian consent to
      publication and future commercial use. No artist name or age is published.
- [ ] **OWNER/LEGAL:** trademark clearance for "Super Zayd's Maze Guardians" and character names.
- [ ] **OWNER/LEGAL:** AI-assisted art may have limited standalone copyright protection in the US; review
      before registering or licensing.
- [x] Publishing a first name ("Zayd") in the title is the owner's choice; no surname, age, school,
      photo or location is published anywhere on the site.
- [x] No advertising, purchases, sweepstakes or dark patterns. Before monetising, follow FTC rules on
      advertising to children and the CARU guidelines, and clearly separate ads from content.

## F. Changes that require a new review **before** shipping

Accounts · payments/subscriptions · newsletters or any email collection · contact forms · comments or
fan-art uploads · analytics of any kind · ads · social embeds · reader-facing AI · the Java backend going
public · native apps · contests. Each of these may require verifiable parental consent, new notices and
security/retention programs.

## G. Accessibility (WCAG 2.2 AA target)

| Item | Status |
| --- | --- |
| Landmarks, single `h1` per page, logical headings, `lang="en"` | ✅ |
| Skip link, visible focus ring (yellow + ink), focus moved to `<main>` after navigation | ✅ |
| Reader fully keyboard-operable (buttons, ← → keys, panel dots), live "Panel N of 12" announcement | ✅ |
| Every image has alt text; dialogue is real text, not baked into images; handwritten words described in alt | ✅ |
| Colour contrast ≥ 4.5:1 for body text (ink on cream/white, white/yellow on purple) | ✅ by palette design |
| Target size ≥ 24 × 24 px (2.5.8): dots 30 px, buttons ≥ 40 px | ✅ |
| `prefers-reduced-motion` respected; no autoplay, flashing or sound | ✅ |
| Reflow at 320–375 px with no horizontal scroll | ✅ E2E-tested at 375 px |
| Manual screen-reader pass (VoiceOver/NVDA) by a person | ⏳ **OWNER**: recommended before launch |

## H. Security

- [x] Strict CSP (`default-src 'self'`, no inline script/style, `frame-ancestors 'none'`, `form-action 'none'`).
- [x] `Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`,
      `Cross-Origin-Opener-Policy`, restrictive `Permissions-Policy`, HSTS (`.dev` is HSTS-preloaded).
- [x] No secrets in the repository; static hosting only; two runtime dependencies (React, React DOM).
- [ ] **OWNER:** enable Dependabot alerts on GitHub and two-factor authentication on GitHub and Cloudflare.
