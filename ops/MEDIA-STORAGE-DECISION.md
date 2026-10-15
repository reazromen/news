# Media storage decision

- Canonical publication: Git Markdown + Git commit; no separate news-content database.
- Image binary storage: external media storage/CDN (Cloudinary or `images.reazromen.com`) only after credentials, retention, backup, and delivery URLs are verified.
- The news repository holds image references and rights metadata; large media binaries do not belong in Git history.
- Until an image host is configured and rights are recorded, articles ship without a local copy of the newspaper image.
- Attribution is mandatory when required but is not a substitute for copyright permission.

Implementation status: policy documented; automated rights gate and media upload are not yet connected to n8n. Do not claim image ingestion is live until an end-to-end test proves it.
