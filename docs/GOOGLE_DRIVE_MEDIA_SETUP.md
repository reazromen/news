# Google Drive media storage setup

## Storage contract

- Google Drive folder: `NewsMedia/approved/` for rights-cleared image binaries.
- Each binary has a matching `<asset-id>.rights.json` provenance record in the same folder.
- Asset ID defaults to the first 16 characters of the SHA-256 digest, allowing duplicate detection.
- The uploader refuses incomplete rights information. Permission-based uploads require an internal permission reference; licence-based uploads require an HTTPS licence URL.
- Uploads remain private by default. Public sharing is not enabled by the script.
- Git stores article text and the rights/asset metadata; it does not store image binaries.

## One-time authorization

On the server, run `rclone config` as the `romen` user and create a Google Drive remote named `newsdrive`. Complete Google's OAuth flow in the browser as prompted. Keep the rclone config private; never commit it to Git or paste its token into chat. Verify access with `rclone lsd newsdrive:` and create `NewsMedia/approved/` if needed.

## Upload

Use `python3 scripts/upload_image_to_drive.py --help` for the full argument list. The tool requires source, credit, licence/permission basis, reviewer, alt text, and caption. It uploads the binary and rights manifest, but intentionally does not make the file public.

## Website delivery

Drive storage is not automatically a production CDN. Before placing any Drive URL in a published article, verify that the specific file has the intended sharing permission, that an unauthenticated browser can load it as an image, and that the delivery URL is stable and respects Google's quotas. Keep files private until an editor explicitly approves public delivery. If direct Drive rendering proves unreliable, retain Drive as the archive and add a delivery proxy/CDN later without moving the canonical article content out of Git.

## Current state

Uploader and policy are prepared. Google OAuth is not configured until the server owner completes `rclone config`; public image delivery remains unenabled until tested.
