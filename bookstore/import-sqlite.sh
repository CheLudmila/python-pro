#!/bin/sh
set -eu

: "${SQLITE_IMPORT_PATH:?Set SQLITE_IMPORT_PATH to the mounted SQLite file}"
: "${POSTGRES_HOST:?Set POSTGRES_HOST to the destination PostgreSQL server}"
test -f "$SQLITE_IMPORT_PATH"
export PYTHONUTF8=1

fixture_dir=$(mktemp -d)
trap 'rm -rf "$fixture_dir"' EXIT

# Match Django metadata and the seeded group by natural key.
python manage.py dumpdata contenttypes auth --database=sqlite_import --all \
    --natural-foreign --natural-primary --output "$fixture_dir/metadata.json"
python manage.py dumpdata --database=sqlite_import --all \
    --natural-foreign --exclude contenttypes --exclude auth \
    --output "$fixture_dir/bookstore.json"

python manage.py migrate --noinput
# Load both fixtures in a single transaction and reset imported primary-key sequences.
python manage.py loaddata "$fixture_dir/metadata.json" "$fixture_dir/bookstore.json"
