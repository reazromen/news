# Git-canonical Bengali News

This repository is the canonical source of published automated news for `news.reazromen.com`. Articles are UTF-8 Markdown files under `content/articles/`; Git commits are the source of truth for the static news corpus. No application database is used for that corpus.

## Publishing architecture

1. The intended pipeline collects candidate source metadata and requests an original Bengali article from the configured AI mesh.
2. Editorial/source validation must check the source URL, dates, required facts, duplicate slug/source, and content quality.
3. Only validated Markdown files may be committed and pushed to `main`.
4. The static-site build/deploy process publishes the Git-canonical article, feed, and sitemap.
5. WordPress is also available on the same hostname and can serve WordPress permalinks and feeds. The WordPress test article documented in [WordPress publishing status](docs/WORDPRESS-PUBLISHING-STATUS.md) was published manually as a one-off verification.

**Important:** The end-to-end Mesh AI → validation → Git → WordPress automation is not yet complete or verified. Do not describe automated WordPress publishing or unattended news scheduling as operational. WordPress-to-Git synchronization is also not implemented.

## Article format

Each `.md` file starts with YAML front matter: `title`, `slug`, `date`, `updated`, `source_name`, `source_url`, `summary`, `category`, and `status: published`. Article body must be original reporting/synthesis, not a close rewrite of one source. Source attribution is rendered on the article page.

## Safety rules

- Max 10 new articles per hourly run; fewer are acceptable if there are not enough unique, verified stories.
- Do not publish if source, date, required facts, or AI output is uncertain.
- Never commit credentials, API keys, WordPress passwords, raw feed dumps, or private data.
- Git commit/push is the publication boundary for the static news corpus. A draft or failed validation must not be included in a production commit.
- Do not enable unattended publishing until an actual end-to-end test passes.
- WordPress is not removed by this project. Git remains canonical for the static news corpus unless an explicit, documented architecture change is approved.

## Current deployment state

The static homepage is served at https://news.reazromen.com/. A two-minute poll deploys pushed commits to the dedicated static directory and refuses to deploy if the checkout has uncommitted changes. Caddy serves matching static files first and falls back to WordPress for WordPress routes and non-static permalinks. The root homepage remains static.

For the latest known WordPress test result, route behavior, and activation gates, see [docs/WORDPRESS-PUBLISHING-STATUS.md](docs/WORDPRESS-PUBLISHING-STATUS.md) and [ops/IMPLEMENTATION-STATUS.md](ops/IMPLEMENTATION-STATUS.md).

## Image policy

Read [docs/IMAGE_RIGHTS_AND_STORAGE.md](docs/IMAGE_RIGHTS_AND_STORAGE.md). A newspaper credit does not grant permission to rehost its copyrighted image. Publish hosted images only when a documented licence, permission, public-domain basis, or permitted press-kit use is recorded. Image binaries belong in a verified media host/CDN, not the news Git history; Git stores the URL and rights metadata.
