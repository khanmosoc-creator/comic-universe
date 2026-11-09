# Owner approval workflow for new illustrations

All content is created **offline** by the owner (or tools the owner runs). Nothing is generated in the
reader's browser, and readers can never upload or submit art.

```
 sketch / idea ─▶ prepare (process_owner_art.py or generate_art.py) ─▶ preview locally ─▶
 owner review checklist ─▶ record in asset-manifest.json ─▶ pull request ─▶ CI build ─▶ merge ─▶ Cloudflare deploy
```

## 1. Prepare

* **Owner sketches:** save the original outside the repo, then run
  `python3 tools/art/process_owner_art.py <originals-folder> apps/web/public/art/owner`
  (add the new file to the `SOURCES` map first). This strips all metadata.
* **Studio art:** add or change a function in `tools/art/generate_art.py`, then
  `python3 tools/art/generate_art.py apps/web/public/art`.
* **AI image tools (if ever used):** use only tools whose terms grant the owner commercial rights, never
  prompt with other creators' character names, styles-as-names or logos, and keep the prompt and tool
  name in the manifest entry.

## 2. Owner review checklist (all must be "yes")

- [ ] Original: does not resemble any existing character, costume, logo, setting or artwork.
- [ ] Kid-appropriate: no gore, real weapons, scary realism, unsafe stunts or mean-spirited jokes.
- [ ] Privacy: no real child's face, photo, full name, age, school, address, uniform or location clues.
      **Photographs of children are not published** without a written, specific parental permission.
- [ ] Rights: the owner holds the rights (or has written permission from the artist / their guardian).
- [ ] Accessibility: alt text written in the content JSON; text in art also appears as real text.
- [ ] Metadata stripped (the scripts do this; verify with `exiftool` or PIL if adding files by hand).

## 3. Record

Add an entry to `docs/asset-manifest.json` (path, source, origin, processing, rights, `approval` with the
date and owner's name, `aiGenerated`). Regenerate hashes with the snippet in the manifest history or by
re-running the generator script.

## 4. Publish

Open a pull request → `web-ci` type-checks and builds → Cloudflare Pages builds a **preview URL** for the
PR → the owner reviews the preview → merge to `main` → Cloudflare deploys production.

## Removing art

Delete the file and its manifest entry, remove references in `apps/web/src/content/*.json`, merge. Cloudflare
serves only the latest deployment; older preview deployments can be deleted in the Pages dashboard.
