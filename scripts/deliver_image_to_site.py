#!/usr/bin/env python3
"""Explicitly deliver a rights-cleared Drive image to the public news media path."""
import argparse
import hashlib
import json
import mimetypes
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_BASES = {"license", "permission", "public-domain", "press-kit", "original"}

def run(args):
    return subprocess.run(args, text=True, capture_output=True, check=True).stdout

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--asset-id", required=True)
    p.add_argument("--remote", default="newsdrive:NewsMedia/approved")
    p.add_argument("--site-root", type=Path, default=Path("/home/romen/services/hserver-caddy/www/news"))
    p.add_argument("--public-base", default="https://news.reazromen.com/media")
    p.add_argument("--approve-public-delivery", action="store_true",
                   help="Explicitly approve serving this asset publicly on news.reazromen.com")
    a = p.parse_args()
    if not a.approve_public_delivery:
        p.error("refusing to publish: pass --approve-public-delivery only after editorial approval")
    asset_id = re.sub(r"[^a-zA-Z0-9._-]+", "-", a.asset_id).strip("-")
    if not asset_id or asset_id != a.asset_id:
        p.error("--asset-id contains unsupported characters")
    remote = a.remote.rstrip("/")
    manifest_remote = f"{remote}/{asset_id}.rights.json"
    try:
        manifest = json.loads(run(["rclone", "cat", manifest_remote]))
    except Exception as exc:
        p.error(f"could not read rights manifest from Drive: {exc}")
    required = ("drive_path", "sha256", "source_url", "source_name", "credit_line",
                "license", "rights_basis", "rights_checked_by", "alt", "caption")
    missing = [key for key in required if not str(manifest.get(key) or "").strip()]
    if missing:
        p.error(f"rights manifest is incomplete: {missing}")
    if manifest["rights_basis"] not in ALLOWED_BASES:
        p.error("rights basis is not approved for public delivery")
    if not manifest["source_url"].startswith("https://"):
        p.error("rights manifest source URL must use HTTPS")
    if manifest["rights_basis"] == "permission" and not manifest.get("permission_reference"):
        p.error("permission-based asset has no permission reference")
    if manifest["rights_basis"] == "license" and not str(manifest.get("license_url") or "").startswith("https://"):
        p.error("licensed asset has no HTTPS licence URL")
    if manifest["rights_basis"] == "original" and not str(manifest.get("creator") or "").strip():
        p.error("original artwork must identify its creator")
    filename = Path(urlparse(manifest["drive_path"]).path).name
    if not filename or filename in {".", ".."} or "/" in filename or "\\" in filename:
        p.error("unsafe file name in rights manifest")
    media_dir = a.site_root.resolve() / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    destination = media_dir / filename
    created = False
    try:
        with tempfile.TemporaryDirectory(prefix="news-media-delivery-") as temp:
            local = Path(temp) / filename
            run(["rclone", "copyto", manifest["drive_path"], str(local)])
            digest = hashlib.sha256(local.read_bytes()).hexdigest()
            if digest.lower() != str(manifest["sha256"]).lower():
                p.error("downloaded file SHA-256 does not match the rights manifest")
            if destination.exists():
                current = hashlib.sha256(destination.read_bytes()).hexdigest()
                if current != digest:
                    p.error(f"destination already exists with different content: {destination}")
            else:
                shutil.copy2(local, destination)
                destination.chmod(0o644)
                created = True
            url = f"{a.public_base.rstrip('/')}/{filename}"
            manifest["public_delivery_url"] = url
            manifest["sharing_status"] = "public-on-site"
            manifest["public_delivery_at"] = datetime.now(timezone.utc).isoformat()
            manifest["public_sha256_verified"] = digest
            manifest_path = Path(temp) / f"{asset_id}.rights.json"
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            try:
                run(["rclone", "copyto", str(manifest_path), manifest_remote])
            except Exception:
                if created:
                    destination.unlink(missing_ok=True)
                raise
            print(json.dumps({
                "asset_id": asset_id, "public_delivery_url": url,
                "sha256": digest, "size_bytes": destination.stat().st_size,
                "content_type": mimetypes.guess_type(filename)[0] or "application/octet-stream",
                "sharing_status": manifest["sharing_status"], "rights_basis": manifest["rights_basis"]
            }, ensure_ascii=False, indent=2))
    except subprocess.CalledProcessError as exc:
        p.error("delivery failed; check rclone authorization and Drive path: " + (exc.stderr or exc.stdout or str(exc)))

if __name__ == "__main__":
    main()
