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

The repository and static build workflow are prepared. The custom domain must only be switched after GitHub Pages deployment is verified, and DNS/edge routing must be changed deliberately so the existing WordPress site is not accidentally disrupted. AI-provider and n8n credentials are configured separately from this repository.
