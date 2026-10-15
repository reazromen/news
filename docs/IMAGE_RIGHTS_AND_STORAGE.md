# News image rights, attribution, and storage

## Editorial rule

A newspaper's image is copyrighted by default. Naming the newspaper or photographer is attribution, not permission. Do not download, mirror, crop, rehost, or publish a copyrighted image solely because a credit line is added. Before publication, record a documented permission or licence that covers the intended use, or use a permitted embed/link instead of copying the file.

Allowed sources, in preference order:

1. Images explicitly licensed for reuse (verify the exact licence and its conditions).
2. Images supplied with written permission by the publisher, photographer, agency, organization, or rights holder.
3. Official press/media kits whose terms allow this use.
4. Public-domain images, after verifying the status and jurisdiction.
5. An embed or link to the original publisher's page where the publisher's own player/image is served under its terms; do not bypass paywalls or hotlink in violation of terms.
6. Original commissioned or generated illustrations, labelled accurately and never presented as documentary evidence.

If permission or licence is unclear, publish without the image. Never remove watermarks, bypass access controls, or imply that a credit alone clears rights. Follow any licence-specific requirements, including attribution wording, link, share-alike, and non-commercial restrictions. Flag editorial/legal review where rights are disputed.

## Storage design

- Git stores Markdown, source metadata, image metadata, and small original/licensed assets only when appropriate. Do not commit scraped newspaper image collections or large binary files to the article repository.
- Store approved image binaries in the media bucket/CDN (preferred: Cloudinary or the existing `images.reazromen.com` media origin after access, backup, and retention are verified). Keep the provider asset ID and stable delivery URL in the article front matter. Do not put API secrets in Git.
- If no approved media storage is configured, link/embed the source rather than silently writing image files to the server's root disk. Server disk is already a constrained resource and is not the default media archive.
- Use immutable filenames/asset IDs, preserve the original file where licence allows, and record SHA-256 for provenance and duplicate detection. Keep a backup/export of approved assets and their rights metadata.

## Required metadata for every image

Record these fields in the article front matter or an adjacent `content/media/<asset-id>.yml` record:

- `asset_id`: stable ID or provider ID
- `url`: published delivery URL, if hosted
- `source_name`: newspaper, agency, photographer, or rights holder
- `source_url`: exact original image/article page
- `creator`: photographer/creator, if credited
- `credit_line`: exact required credit text
- `license`: licence name/version or `permission`
- `license_url`: licence terms or written permission reference (never expose private correspondence)
- `permission_reference`: internal ticket/document ID where applicable
- `retrieved_at`: UTC timestamp
- `sha256`: file hash where a local copy is authorized
- `alt`: factual accessibility text
- `caption`: factual caption, including place/date only when verified
- `rights_checked_by` and `rights_checked_at`

## Article integration

An image may be displayed only when the article's image record has a verified rights basis. Render a visible caption/credit and link to the source where appropriate. Do not treat an RSS thumbnail URL as a licence. Do not infer that images are reusable just because they are accessible without login.

## Automation gate

The publishing workflow must reject or omit an image when the rights basis, source URL, credit line, or licence/permission evidence is missing. It must not scrape full-size images by default. Store only the article text and source metadata needed for editorial work; keep the original article linked. An editor can approve an image record before a Git commit publishes it.
