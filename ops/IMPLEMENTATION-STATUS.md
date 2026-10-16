# Implementation status

Last updated: 2026-10-16

## Completed in this repository

- Dedicated public Git repository for canonical news source.
- Static-site builder with no database dependency.
- Build-and-deploy GitHub Actions workflow.
- Source attribution, canonical URLs, RSS feed, sitemap, and slug/source duplicate checks.
- Build rejects articles without required metadata, HTTPS source URLs, explicit timezone, or minimum body length.
- A two-minute host poll deploys the Git-built static site and refuses to deploy when the checkout has uncommitted changes.
- Image metadata validation requires source URL, alt text, caption, credit, licence/permission basis, and explicit rights-check flag.
- Google Drive image archival and explicit public-delivery scripts exist. One original editorial SVG was delivered to `/media/` and verified publicly with HTTP 200 and matching SHA-256.

## Live and verified (2026-10-16)

- `https://news.reazromen.com/` serves the Git-built static homepage over HTTPS.
- `/feed.xml` and `/sitemap.xml` return HTTP 200.
- Static article `/article/dhaka-shyamapur-to-cumilla-81km-rail-cord-line-proposal/` returns HTTP 200.
- WordPress post ID 680 is published at `https://news.reazromen.com/dhaka-shyamapur-to-cumilla-81km-rail-cord-line-proposal/`.
- WordPress REST API reported post 680 as published; WordPress RSS and category archive included it.
- Caddy serves existing static files first and falls back to WordPress for non-static permalinks and WordPress routes.
- The authenticated WordPress MU plugin now exposes a direct-publish endpoint plus the retained draft-only endpoint; PHP syntax validation passed.
- n8n smoke workflow fetched the approved Git article, validated it, and created WordPress draft post ID 681 with a test-only title/slug.
- Retrying the same request returned post ID 681 with `idempotent_replay=true`; no duplicate draft was created.
- Unauthenticated publisher access returned HTTP 401. Anonymous draft permalink returned HTTP 404.
- The temporary test webhook was unpublished; n8n main was restarted, and the route returned HTTP 404 afterward.
- Public homepage and existing published article continued returning HTTP 200.

Detailed evidence and limitations: [WordPress publishing status](../docs/WORDPRESS-PUBLISHING-STATUS.md).

## Publisher implementation

- WordPress MU plugin source: `/home/romen/services/news-portal/ops/news-publisher-draft-api.php`.
- Direct endpoint: `POST /wp-json/news-publisher/v1/publish`; retained safe draft endpoint: `/wp-json/news-publisher/v1/draft`.
- Auth header: `X-News-Publisher-Token`; the token lives in the protected WordPress environment file and an encrypted n8n credential, not in workflow JSON or Git.
- The direct endpoint publishes only after validating the submitted approved Git article; the draft endpoint remains draft-only. Both validate input, restrict image embeds to approved site media, reject slug conflicts, and handle idempotent retries.
- Permanent n8n workflow: `News Git → WordPress Direct Publisher (Manual Only)`; it is inactive and has no schedule trigger. It now targets `/publish`.
- The one-article test passed using a temporary authenticated webhook workflow, which is now inactive.

## Not yet enabled / incomplete

- The full Mesh AI → source/editorial validation → Git commit/deploy → WordPress pipeline has not passed an end-to-end automated test.
- Current n8n publisher workflow reads one fixed approved Git article; it is not yet a dynamic queue or connected to the Mesh AI generation stage.
- Hourly/unattended news generation and publishing are not approved for activation.
- WordPress-to-Git export/synchronization and conflict handling are not implemented.
- Image ingestion/upload is not connected to the news n8n workflow.
- Google Drive OAuth/client configuration must be reviewed before unattended use; do not put tokens in repository files or workflow exports.

## Next safe activation order

1. Connect Mesh AI generation and source verification to the validated article queue.
2. The Git article directory currently contains only one article, already published as WordPress post 680. Prepare and approve a distinct article with a new unused slug before running the direct-publish workflow; never overwrite post 680.
3. Run the permanent publisher workflow manually and verify published status, public permalink, metadata, media, RSS/category inclusion, and idempotent retry.
4. Add monitored failure handling and ensure drafts are not silently marked published.
5. Keep all schedules and Content Studio global dispatch disabled. Direct publishing is manual-only; do not enable a schedule without separate authorization.
6. Implement explicit WordPress-to-Git export only with conflict detection; Git remains canonical for the static corpus.

## Image rights

A hosted image must have a documented licence, permission, public-domain basis, or other valid rights basis. Attribution alone is not permission to rehost a publisher's image.
