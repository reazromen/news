#!/usr/bin/env bash
set -euo pipefail
REPO=/home/romen/services/news-git-publisher
DEST=/home/romen/services/hserver-caddy/www/news
cd "$REPO"
if [[ -n "$(git status --porcelain)" ]]; then
  echo 'ERROR: news repository has local changes; refusing deployment.' >&2
  exit 2
fi
git fetch --prune origin main
git merge --ff-only origin/main
python3 scripts/build.py --output dist
rsync -a --delete --exclude=/media/ dist/ "$DEST/"
printf 'Deployed commit %s to %s\n' "$(git rev-parse --short HEAD)" "$DEST"
