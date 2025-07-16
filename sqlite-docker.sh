#!/bin/bash

# Helper script for running SQLite commands in the Docker container

DB_FILE=${1:-"proref.db"}
SQL_COMMAND=${2:-".tables"}

echo "Running command: $SQL_COMMAND on database: $DB_FILE"
# The alpine/sqlite container doesn't accept commands directly
# We need to run sqlite3 and then pass the commands
docker exec -i fuzeteai-sqlite /bin/sh -c "echo \"$SQL_COMMAND\" | sqlite3 /data/$DB_FILE"
