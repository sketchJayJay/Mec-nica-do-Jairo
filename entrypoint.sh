#!/bin/sh
set -e
mkdir -p "$(dirname "${DATABASE_PATH:-/data/oficina.db}")"
exec "$@"
