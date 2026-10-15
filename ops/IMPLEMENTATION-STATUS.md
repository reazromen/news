# Implementation status

Last updated: 2026-10-16

## Completed in this repository

- Created a dedicated public Git repository for canonical news source.
- Added a static-site builder with no database dependency.
- Added build-and-deploy GitHub Actions workflow.
- Added source attribution, canonical URLs, RSS feed, sitemap, and slug/source duplicate checks.
- Build rejects articles without required metadata, HTTPS source URLs, explicit timezone, or minimum body length.
- A two-minute host poll deploys the Git-built static site and refuses to deploy when the checkout has uncommitted changes.
- Image metadata validation requires a source URL, alt text, caption, credit, licence/permission basis, and explicit rights-check flag whenever an image is included.
- Google Drive image archival and explicit public-delivery scripts exist. One original editorial SVG was delivered to `/media/` and verified publicly with HTTP 200 and matching SHA-256.

## Live and verified (2026-10-16)

- `https://news.reazromen.com/` serves the Git-built static homepage over HTTPS.
- `/feed.xml` and `/sitemap.xml` return HTTP 200.
- Static article `/article/dhaka-shyamapur-to-cumilla-81km-rail-cord-line-proposal/` returns HTTP 200.
- WordPress post ID 680 is published at `https://news.reazromen.com/dhaka-shyamapur-to-cumilla-81km-rail-cord-line-proposal/`.
- WordPress REST API reported the post as published with the expected permalink and category metadata; WordPress RSS included the post; the category archive returned HTTP 200 and included it.
- The test post body contains the approved conceptual SVG illustration and source links; the public image returned HTTP 200.
- Caddy configuration was validated and reloaded after routing was changed to serve existing static files first and fall back to WordPress for non-static permalinks and WordPress routes.
- The root homepage remains static. WordPress article permalinks and WordPress RSS are available separately.
- Detailed evidence and limitations are recorded in [WORDPRESS-PUBLISHING-STATUS.md](../docs/WORDPRESS-PUBLISHING-STATUS.md).

## Important distinction: manual test vs automation

The WordPress post was inserted as a one-off manual test using a temporary PHP script and the WordPress bootstrap. **This proves the post can exist and be served by WordPress; it does not prove an automated publisher works.** The temporary script is not a maintained production integration.

## Not yet enabled / incomplete

- The full Mesh AI → source/editorial validation → Git commit/deploy → WordPress publishing flow has not passed an end-to-end automated test.
- A reusable WordPress publisher with secret handling, field mapping, idempotency, retries, and duplicate recovery is not yet connected to n8n.
- WordPress-to-Git export/synchronization and conflict handling are not implemented.
- Hourly/unattended news generation and publishing are not approved for activation.
- Image ingestion/upload is not connected to the news n8n workflow.
- Google Drive OAuth/client configuration must be reviewed before unattended use; do not put tokens in repository files or workflow exports.

## Next safe activation order

1. Inspect the existing n8n/news workflow and provider health; do not enable schedules while the AI quality/provider test is failing.
2. Implement a narrowly scoped WordPress publisher using approved secret storage and validated article inputs only.
3. Add idempotency, draft-first mode, and clear failure/retry behavior.
4. Test a single article through the real automation path, then verify the REST API, permalink, RSS/category visibility, image delivery, and no-duplicate retry behavior.
5. Keep global/scheduled dispatch disabled until the owner explicitly approves after reviewing passing test evidence.
6. Implement explicit WordPress-to-Git export only with conflict detection; Git remains canonical for the static corpus.

## Image rights

The image rights policy, Google Drive uploader, and explicit public-delivery script are implemented. A hosted image must have a documented licence, permission, public-domain basis, or other valid rights basis; attribution alone is not permission to rehost a publisher's image.
