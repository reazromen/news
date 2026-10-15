# Implementation status

## Completed in this repository
- Created a dedicated public Git repository for canonical news source.
- Added a static-site builder with no database dependency.
- Added build-and-deploy GitHub Actions workflow.
- Added source attribution, canonical URLs, RSS feed, sitemap, and slug/source duplicate checks.
- Build rejects articles without required metadata, HTTPS source URLs, explicit timezone, or minimum body length.
- WordPress has not been removed, migrated, or modified.

## Not yet enabled
- GitHub Pages deployment/custom-domain DNS cutover must be verified before switching `news.reazromen.com` away from WordPress.
- Hourly n8n AI generation, source-quality validation, Git commit/push, and WordPress-to-Git manual-edit sync are not live yet.
- The current AI mesh providers have previously returned cooldown/unavailable states; recheck before activating an unattended workflow.

## Safe activation order
1. Verify GitHub Pages build/deployment.
2. Verify the Pages origin over HTTPS and confirm the `CNAME`/domain configuration.
3. Configure DNS/Cloudflare routing only after the static origin is verified; preserve WordPress under a separate admin hostname or route.
4. Connect n8n to a narrowly scoped publisher service/credential. Never store credentials in the workflow JSON or article repo.
5. Run dry-run tests, then a single article test, before enabling hourly runs.
6. Implement WordPress manual-edit export as an explicit Git commit, with conflict detection. Git commit remains canonical.
