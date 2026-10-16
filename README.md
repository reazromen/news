# Git-canonical Bengali News

This repository is the canonical source of published news for `news.reazromen.com`. Articles are UTF-8 Markdown files under `content/articles/`; Git commits are the source of truth for the static news corpus. No application database is used for that corpus.

## Publishing architecture

1. The intended pipeline collects candidate source metadata and requests an original Bengali article from the configured AI mesh.
2. Editorial/source validation checks source URLs, dates, required facts, duplicate slug/source, and content quality.
3. Only validated Markdown files may be committed and pushed to `main`.
4. The static-site build/deploy process publishes the Git-canonical article, feed, and sitemap.
5. A draft-only WordPress endpoint and n8n workflow now support delivery of an approved Git article to WordPress for editorial review.

**Current verified boundary:** one approved Git article was fetched by n8n and created as WordPress draft ID 681. A retry returned the same draft ID without duplication. The already-live canonical WordPress article (post 680) was left unchanged. This verifies one-article Git → validation → n8n → WordPress draft delivery, not the full unattended Mesh AI generation pipeline.

**Do not enable scheduled publishing yet.** The permanent publisher workflow is inactive and manual-only. The Mesh AI generation/source-verification stage is not yet connected to a dynamic approved-article queue. WordPress-to-Git synchronization is also not implemented.

## Article format

Each `.md` file starts with YAML front matter: `title`, `slug`, `date`, `updated`, `source_name`, `source_url`, `summary`, `category`, and `status: published`. Article body must be original reporting/synthesis, not a close rewrite of one source. Source attribution is rendered on the article page.

## Safety rules

- Max 10 new articles per hourly run; fewer are acceptable if there are not enough unique, verified stories.
- Do not publish if source, date, required facts, or AI output is uncertain.
- Never commit credentials, API keys, WordPress passwords, raw feed dumps, or private data.
- Git commit/push is the publication boundary for the static news corpus. A draft or failed validation must not be included in a production commit.
- The WordPress publisher endpoint is draft-only, rejects slug conflicts, and is idempotent for a repeated draft with the same source.
- Do not enable unattended publishing until an actual end-to-end test passes and the owner explicitly authorizes activation.
- WordPress is not removed by this project. Git remains canonical for the static news corpus unless an explicit, documented architecture change is approved.

## Current deployment state

The static homepage is served at https://news.reazromen.com/. A two-minute poll deploys pushed commits to the dedicated static directory and refuses to deploy if the checkout has uncommitted changes. Caddy serves matching static files first and falls back to WordPress for WordPress routes and non-static permalinks. The root homepage remains static.

For the endpoint, test evidence, route behavior, and activation gates, see [docs/WORDPRESS-PUBLISHING-STATUS.md](docs/WORDPRESS-PUBLISHING-STATUS.md), [ops/IMPLEMENTATION-STATUS.md](ops/IMPLEMENTATION-STATUS.md), and the server operations guide `/home/romen/services/news-portal/ops/NEWS-WORDPRESS-PUBLISHER.md`.

## Image policy

Read [docs/IMAGE_RIGHTS_AND_STORAGE.md](docs/IMAGE_RIGHTS_AND_STORAGE.md). A newspaper credit does not grant permission to rehost its copyrighted image. Publish hosted images only when a documented licence, permission, public-domain basis, or permitted press-kit use is recorded. Image binaries belong in a verified media host/CDN, not the news Git history; Git stores the URL and rights metadata.
