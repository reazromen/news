# WordPress → Git-canonical static news sync

Last updated: 2026-10-16

## Contract

WordPress is the editorial publishing interface; Git remains the canonical static corpus. A published WordPress post is imported into `content/articles/<slug>.md`, committed and pushed to `origin/main`; the existing two-minute local deploy poll rebuilds the homepage, article pages, RSS feed, and sitemap from Git. Caddy continues serving the static site first and WordPress for admin/API routes and non-static fallbacks.

## Import guardrails

- The initial cutover watermark is WordPress post ID `681` (exclusive). This deliberately excludes the existing WordPress archive and test draft ID 681; only newly created posts with ID > 681 are candidates.
- Only WordPress posts whose REST status is `publish` are considered. Drafts and pending posts are never imported.
- Slugs must be lowercase ASCII words separated by hyphens, matching the static builder's URL contract.
- The article body must contain at least 250 characters and at least one external HTTPS source link. Posts failing these checks are logged and skipped.
- Existing Git slugs are immutable. A matching slug is never overwritten by WordPress content.
- Images and captions are omitted during import. An image must pass the separate image-rights workflow before it can be added to Git metadata.
- The importer refuses to run with uncommitted changes in the Git checkout, and uses a lock in cron to avoid concurrent imports.
- A successful import is committed and pushed. If push fails, the script reports failure; the next run retries a pending local commit only when `origin/main` is an ancestor of local `HEAD`. Divergence stops the importer for manual reconciliation.

## Cutover and validation

- `scripts/sync_wordpress_published.py --dry-run` checks the live public WordPress REST API without writing files.
- `python3 -m unittest discover -s tests -v` runs parser/validation tests.
- The importer does not backfill historic WordPress posts. The pre-existing Git article (WordPress post 680) stays owned by Git and is not overwritten.
- If a new post lacks a valid external HTTPS source link, uses a non-ASCII slug, or has too little body text, it remains available in WordPress but is not copied to the static site; inspect the sync log and fix the source post before retrying.
- The `news-wordpress-git-sync` cron entry runs every two minutes on odd minutes. The existing static deployment poll runs on even minutes, so a successful Git push is normally deployed on the next poll.
- No WordPress content is deleted or modified by this importer. It only creates new Markdown files for previously unseen slugs.

## Operations

```sh
python3 /home/romen/services/news-git-publisher/scripts/sync_wordpress_published.py --dry-run
python3 -m unittest discover -s /home/romen/services/news-git-publisher/tests -v
```

Log: `/home/romen/logs/news-wordpress-git-sync.log`

Backups captured before this change: `/home/romen/services/hserver-caddy/backups/news-sync-prechange-20261016-1128/` (Caddyfile, static site, WordPress database dump, and MU plugins; SHA-256 manifest included).
