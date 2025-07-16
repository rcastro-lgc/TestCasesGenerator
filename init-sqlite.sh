#!/bin/sh
set -e

echo "Starting SQLite container initialization..."
mkdir -p /data
echo "Created data directory"
touch /data/proref.db
echo "Created database file"
echo ".databases" | sqlite3 /data/proref.db
echo "Initialized database"
echo "Initialization complete, keeping container alive..."

# Keep container running
exec tail -f /dev/null
