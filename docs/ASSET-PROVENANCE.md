# Copyright & licence provenance

Machine-readable inventory with file hashes: [`asset-manifest.json`](asset-manifest.json).

## 1. Owner-supplied sketches (5 files × WebP + PNG)

| Published slug | Owner upload | Used in |
| --- | --- | --- |
| `stretch-punch` | `canvas_5.png` | Issue #1 panel 4 · Art Vault · Dragoncrest profile |
| `stretch-punch-replay` | `canvas_4.png` | Issue #1 panel 5 · Art Vault |
| `robo-beast-roar` | `canvas.png` | Issue #1 panel 3 · Art Vault · Grumblejaw profile |
| `wave-ride` | `canvas_3.png` | Issue #1 panel 7 · Art Vault · Zigzag and Splashfang profiles |
| `yeti-showdown` | `canvas_1.png` | Issue #1 panel 8 · Art Vault · Arrowlight, Bubbleguard and Blizzardbyte profiles |

* Supplied by the site owner on 2026-11-09 with an explicit request to include them on the public site.
* Processing (`tools/art/process_owner_art.py`) flattens, trims blank margins, resizes and **removes all
  metadata** (EXIF/XMP, device or location data). No drawn content was altered.
* They are hand drawings, not photographs, and contain no faces, names, schools or locations.
* **Owner to confirm:** that the owner holds the rights to these drawings, and — if they were drawn by a
  child — that the parent/guardian consents to publication and to any future commercial use. Credit is
  given generically ("junior art department"); no artist's name or age is published.

## 2. Studio art (AI-assisted, original) — 20 files

Hero and villain portraits, Issue #1 cover, panels 1, 2, 6, 9, 10, 11, 12, the home banner, the Mazeverse
map, the Z badge/favicon and the social card were produced by `tools/art/generate_art.py`, which draws every
shape from hand-written coordinates (circles, paths, polygons). No image, character, costume, logo or
artwork from any third party was used as input, traced, or referenced.

* Characters and setting are original: Super Zayd, Dragoncrest, Arrowlight, Bubbleguard, Zigzag,
  Grumblejaw, Blizzardbyte, Splashfang, the Glitchlings, the Mazeverse and its places. Generic genre
  elements only (capes, masks, a bow, a force-field, speed lines, a yeti, a sea serpent, a robot).
* Several designs are developed from the owner's sketches (see table above), which is the owner's own IP.
* **Note on AI-assisted works:** in the US, purely AI-generated material may not be eligible for copyright
  registration on its own; the owner's creative selection, arrangement and the human-authored sketches,
  story and characters are. Get legal advice before registering copyrights or trademarks or licensing the
  characters commercially. These files are marked "pending owner sign-off" in the manifest until the owner
  completes the approval workflow.

## 3. Fonts

Poppins (Regular, Bold, Bold Italic) — Copyright 2020 The Poppins Project Authors — SIL Open Font
License 1.1. Subset to Latin and served from `/fonts/` with the licence text (`/fonts/OFL.txt`).
The full TTFs used for outlining SVG lettering live in `tools/art/fonts/` with the same licence.

## 4. Code

All site and backend code is original to this repository. Runtime dependencies: React and React DOM
(MIT). Build tooling: Vite, @vitejs/plugin-react, TypeScript (MIT / Apache-2.0). Optional backend:
Spring Boot (Apache-2.0).

## 5. Names and trademarks — owner/legal review

"Super Zayd's Maze Guardians" and the character names have **not** been searched or cleared as trademarks.
Before commercial launch (merchandise, app stores, paid comics) run a USPTO and common-law clearance search
and consider registration.
