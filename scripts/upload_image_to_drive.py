#!/usr/bin/env python3
"""Upload a rights-cleared news image and its provenance record to Google Drive via rclone.

Requires an authenticated rclone remote named `newsdrive` and explicit rights metadata.
Does not make files public automatically; public sharing must be a deliberate editorial action.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_BASES = {"license", "permission", "public-domain", "press-kit", "original"}

def run(args):
    return subprocess.run(args, text=True, capture_output=True, check=True).stdout

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--file", required=True, type=Path)
    p.add_argument("--source-name", required=True)
    p.add_argument("--source-url", required=True)
    p.add_argument("--creator", default="")
    p.add_argument("--credit-line", required=True)
    p.add_argument("--license", required=True)
    p.add_argument("--license-url", default="")
    p.add_argument("--rights-basis", required=True, choices=sorted(ALLOWED_BASES))
    p.add_argument("--permission-reference", default="")
    p.add_argument("--rights-checked-by", required=True)
    p.add_argument("--alt", required=True)
    p.add_argument("--caption", required=True)
    p.add_argument("--asset-id", default="")
    p.add_argument("--remote", default="newsdrive:NewsMedia/approved")
    a = p.parse_args()

    f = a.file.expanduser().resolve()
    if not f.is_file():
        p.error(f"image file does not exist: {f}")
    if not a.source_url.startswith("https://"):
        p.error("--source-url must be HTTPS")
    if not a.license.strip():
        p.error("--license must name the applicable licence or permission basis")
    if a.rights_basis == "original" and not a.creator.strip():
        p.error("--creator is required for original artwork")
    if a.rights_basis == "permission" and not a.permission_reference.strip():
        p.error("--permission-reference is required for permission-based uploads")
    if a.rights_basis == "license" and not a.license_url.startswith("https://"):
        p.error("--license-url must point to the licence terms")

    digest = hashlib.sha256(f.read_bytes()).hexdigest()
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "-", f.name).strip("-") or "image.bin"
    asset_id = a.asset_id.strip() or digest[:16]
    asset_id = re.sub(r"[^a-zA-Z0-9._-]+", "-", asset_id)
    remote = a.remote.rstrip("/")
    image_remote = f"{remote}/{asset_id}-{safe}"
    manifest = {
        "asset_id": asset_id,
        "source_name": a.source_name,
        "source_url": a.source_url,
        "creator": a.creator,
        "credit_line": a.credit_line,
        "license": a.license,
        "license_url": a.license_url,
        "rights_basis": a.rights_basis,
        "permission_reference": a.permission_reference,
        "rights_checked_by": a.rights_checked_by,
        "rights_checked_at": datetime.now(timezone.utc).isoformat(),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "sha256": digest,
        "file_name": f.name,
        "alt": a.alt,
        "caption": a.caption,
        "drive_path": image_remote,
        "public_delivery_url": None,
        "sharing_status": "private-until-explicitly-approved",
    }
    try:
        run(["rclone", "lsjson", a.remote, "--max-depth", "1"])
        run(["rclone", "copyto", str(f), image_remote])
        manifest_path = Path("/tmp") / f"news-media-{asset_id}.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        run(["rclone", "copyto", str(manifest_path), f"{remote}/{asset_id}.rights.json"])
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        print("Upload complete. File remains private; no public link was created.", file=sys.stderr)
    except FileNotFoundError:
        p.error("rclone is not installed or not in PATH")
    except subprocess.CalledProcessError as e:
        p.error("Google Drive upload failed. Check that the newsdrive rclone remote is authenticated; no public sharing was changed. " + (e.stderr or e.stdout or str(e)))

if __name__ == "__main__":
    main()
