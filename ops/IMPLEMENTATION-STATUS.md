# Implementation status

## Completed in this repository
- Created a dedicated public Git repository for canonical news source.
- Added a static-site builder with no database dependency.
- Added build-and-deploy GitHub Actions workflow.
- Added source attribution, canonical URLs, RSS feed, sitemap, and slug/source duplicate checks.
- Build rejects articles without required metadata, HTTPS source URLs, explicit timezone, or minimum body length.
- WordPress has not been removed, migrated, or modified.

## Live and verified
- `news.reazromen.com/` serves the Git-built static homepage over HTTPS.
- `/feed.xml` and `/sitemap.xml` return HTTP 200.
- `/wp-login.php` remains available under the same hostname; `/wp-admin/` redirects unauthenticated visitors to WordPress login.
- Caddy was validated and reloaded after the route change. WordPress was not removed or migrated.
- A user crontab polls the canonical Git repository every two minutes, refuses to deploy with uncommitted local changes, builds the site, and syncs only the dedicated news static directory.
- Image metadata validation now requires a source URL, alt text, caption, credit, licence/permission basis, and explicit rights-check flag whenever an image is included.

## Not yet enabled
- Hourly n8n AI generation, source-quality validation, Git commit/push, and WordPress-to-Git manual-edit sync are not live yet.
- The image rights policy is documented, but image ingestion/upload is not connected to n8n. Newspaper images must not be copied/rehosted without a verified licence or permission; credit alone is insufficient.
- The current AI mesh providers have previously returned cooldown/unavailable states; recheck before activating an unattended workflow.

## Next safe activation order
1. Verify AI mesh generation with a real test and source-quality checks.
2. Connect n8n to a narrowly scoped Git publisher credential. Never store credentials in workflow JSON or the article repo.
3. Run dry-run tests, then one test article commit, before enabling hourly runs (maximum 10, not a forced quota).
4. Configure a media host such as Cloudinary or `images.reazromen.com` only after access, backups, and retention are verified.
5. Implement WordPress manual-edit export as an explicit Git commit, with conflict detection. Git commit remains canonical.
