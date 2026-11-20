#!/usr/bin/env sh
# Creates .env with a random password for the local Postgres container.
# .env is git-ignored. If it already exists, it is left untouched so the
# password keeps matching the running container. If you delete .env and
# create a new one, recreate the container too: docker compose down -v
set -eu

ENV_FILE="$(dirname "$0")/../.env"

if [ -f "$ENV_FILE" ]; then
    echo ".env already exists, leaving it as is."
    exit 0
fi

umask 077
printf 'PGPASSWORD=%s\n' "$(openssl rand -hex 16)" > "$ENV_FILE"
echo "Created .env with a random password (not printed)."
