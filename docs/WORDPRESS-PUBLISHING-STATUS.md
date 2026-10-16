# WordPress publishing status

Last verified: 2026-10-16

## Current result

**The direct-publish endpoint is installed and the permanent n8n workflow is configured for manual direct publishing. No direct publish has yet been executed with a new article. Scheduled news publishing remains disabled.**

### End-to-end draft smoke test

- n8n fetched the approved article Markdown from the Git-canonical GitHub repository.
- The workflow validated the YAML front matter, `status: published`, required metadata, HTTPS source URLs, ASCII slug, and a minimum 250-character body.
- It sent the article to the authenticated WordPress draft-only endpoint.
- WordPress created post ID **681** with status **draft**.
- Test title is prefixed `[AUTOMATION TEST — DRAFT ONLY]`; slug ends with `-publisher-smoke-test`. This avoids touching the already-published live post with the canonical slug.
- The post includes category ID 2, source attribution links, the approved conceptual SVG, source metadata, closed comments, and closed pingbacks.
- A retry returned the same post ID with `idempotent_replay=true`; it did not create a duplicate.
- A request using the already-published canonical slug returned HTTP 409 (`news_publisher_slug_conflict`); post 680 remained `publish`.
- Direct unauthenticated access to the publisher endpoint returned HTTP 401.
- The draft permalink returned HTTP 404 to anonymous visitors, and the anonymous WordPress REST request returned HTTP 401.
- The public homepage and the existing live article continued to return HTTP 200.
- The temporary authenticated webhook used for the smoke test was unpublished. The n8n main service was restarted to unregister the temporary route.

The test draft is intentionally not published. It can be reviewed in WordPress admin at `/wp-admin/post.php?post=681&action=edit`.

## WordPress publisher endpoint

- Source file: `/home/romen/services/news-portal/ops/news-publisher-draft-api.php`
- Installed MU plugin: `/var/www/html/wp-content/mu-plugins/news-publisher-draft-api.php`
- Direct-publish route: `POST /wp-json/news-publisher/v1/publish`; draft-only route remains `POST /wp-json/news-publisher/v1/draft`.
- Authentication: `X-News-Publisher-Token` header; secret is stored in the protected WordPress environment file and in an encrypted n8n credential, not in workflow JSON or Git.
- `/publish` directly publishes a new article after validation; `/draft` remains draft-only. Callers cannot override the post status. Both routes reject conflicting slugs and use idempotency protection.
- It validates required fields, HTTPS source URLs, ASCII slug format, article length, category existence, and approved media URLs under `https://news.reazromen.com/media/`.
- Existing draft with the same slug and source is an idempotent replay. A different or already-published post with the slug is a conflict; the endpoint does not overwrite it.
- Comments and pingbacks are closed. Source links and image caption/alt text are included in the body.
- Backups were taken before the endpoint was installed and before n8n database changes.

## n8n state and activation boundary

- Permanent workflow: `News Git → WordPress Direct Publisher (Manual Only)` (manual trigger only, inactive).
- The one-article smoke-test workflow was used through a temporary authenticated webhook, then unpublished. Its webhook is no longer registered.
- News publishing workflows remain inactive; no schedule node is present in the publisher workflow.
- The Facebook Content Agent remains inactive.
- The unrelated Hserver Infrastructure Sentinel remains active; it is not a news-publishing workflow.
- Content Studio `PUBLISHER_DISPATCH_ENABLED=false` remains a separate safety control and was not enabled.

## What is not complete

This proves **Git article → validation → n8n → WordPress draft** for one approved article. It does not prove a full unattended Mesh AI news pipeline.

Still outstanding:
- The Git article directory currently has only one article and its canonical slug is already live as WordPress post 680. Do not re-run the workflow against that slug; the conflict guard must leave it unchanged.
- Prepare and approve a distinct new Git article with an unused slug, then run the permanent workflow manually and verify WordPress status `publish`, public permalink HTTP 200, source attribution, and idempotent retry.
- Replace the single fixed article URL with a validated queue/trigger that only sends approved canonical articles.
- Test a new, unused canonical slug through the permanent workflow (the existing canonical slug already belongs to a live WordPress post and correctly returns a conflict).
- Add monitored failure alerts and documented retry handling for network/provider failures.
- Test image delivery/rights metadata for more than this one approved original illustration.
- Connect the actual Mesh AI article-generation and source-verification stage to the publisher workflow.
- Keep all schedule triggers and Content Studio global dispatch disabled; direct publishing is currently manual-only.

## Canonical ownership

- Git Markdown remains canonical for the static news corpus.
- WordPress drafts are delivery copies for editorial review, not the source of truth.
- Draft ID 681 is a test-only post with a suffix slug and must remain unpublished.
- WordPress edits are not automatically exported back to Git.
- Do not treat WordPress and Git as dual-authoritative until a conflict-aware export/sync process is implemented.

## Routing

Caddy serves existing Git-built static files first and falls back to WordPress for WordPress routes and non-static permalinks. The root homepage remains static. The Caddy configuration was validated and reloaded after the routing change.

Configuration: `/home/romen/services/hserver-caddy/Caddyfile`

Pre-change backup: `/home/romen/services/hserver-caddy/Caddyfile.pre-wp-permalink-fallback-20261016`
