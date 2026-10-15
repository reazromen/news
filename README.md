# Git-canonical Bengali News

This repository is the canonical source of published automated news for `news.reazromen.com`. Articles are UTF-8 Markdown files under `content/articles/`; Git commits are the source of truth. No application database is used for the automated news corpus.

## Publishing flow

1. n8n gathers RSS metadata and requests an original Bengali article from the configured AI mesh.
2. Validation checks required metadata, source URL, duplicate slug/source URL, date, and minimum content length.
3. Only validated Markdown files are committed and pushed to `main`.
4. GitHub Actions builds a static site and deploys it to GitHub Pages.
5. WordPress remains a separate manual editor. It is not the canonical store for automated articles. Any manual WordPress edit intended to become canonical must be exported as Markdown and committed here before it is treated as authoritative.

## Article format

Each `.md` file starts with YAML front matter: `title`, `slug`, `date`, `updated`, `source_name`, `source_url`, `summary`, `category`, and `status: published`. Article body must be original reporting/synthesis, not a close rewrite of one source. Source attribution is rendered on the article page.

## Safety rules

- Max 10 new articles per hourly run; fewer are acceptable if there are not enough unique, verified stories.
- Do not publish if source, date, required facts, or AI output is uncertain.
- Never commit credentials, API keys, WordPress passwords, raw feed dumps, or private data.
- Git commit/push is the publication boundary. A draft or failed validation must not be included in a production commit.
- WordPress remains available and is not removed or migrated by this project.

## Current deployment state

The static site is served at `https://news.reazromen.com/` from the server-side build of this Git repository. A two-minute poll deploys pushed commits to the dedicated static directory; it refuses to deploy if the checkout has uncommitted changes. WordPress remains available under the same hostname at `/wp-login.php` and `/wp-admin/` for manual editing. Automated AI generation, n8n publishing, image uploads, and WordPress-to-Git export are not yet live.

## Image policy

Read [`docs/IMAGE_RIGHTS_AND_STORAGE.md`](docs/IMAGE_RIGHTS_AND_STORAGE.md). A newspaper credit does not grant permission to rehost its copyrighted image. Publish hosted images only when a documented licence, permission, public-domain basis, or permitted press-kit use is recorded. Image binaries belong in a verified media host/CDN, not the news Git history; Git stores the URL and rights metadata.
