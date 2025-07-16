# Docker Setup for FuzeTestAI

This document provides instructions for setting up and running the FuzeTestAI application using Docker with persistent SQLite storage.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system

## Configuration

The application is configured to use two containers:

1. **SQLite Container** - Uses `alpine/sqlite:3.49.2` image for persistent database storage
2. **Application Container** - Runs the FuzeTestAI application

## Getting Started

### 1. Start the Docker Containers

```bash
docker-compose up -d
```

This will start both the SQLite and application containers in detached mode.

### 2. Verify Containers are Running

```bash
docker ps
```

You should see both containers running (`fuzeteai-sqlite` and `fuzeteai-app`).

### 3. Access the Application

Open your web browser and navigate to:

```
http://localhost:5000
```

## Working with the SQLite Database

The database file is stored in the `./data` directory, which is mounted as a volume in both containers.

### Using the Helper Script

A helper script is provided to interact with the SQLite database:

```bash
# List tables
./sqlite-docker.sh proref.db ".tables"

# Run a query
./sqlite-docker.sh proref.db "SELECT * FROM tickets LIMIT 5;"
```

### Directly Accessing the Database

You can also access the SQLite container directly:

```bash
docker exec -it fuzeteai-sqlite sh
sqlite3 /data/proref.db
```

## Stopping the Containers

```bash
docker-compose down
```

## Data Persistence

The database data is stored in the `./data` directory and persists between container restarts.

## Troubleshooting

### Database Connection Issues

If the application cannot connect to the database, verify:

1. The SQLite container is running
2. The data directory exists and has proper permissions
3. The database file exists in the data directory

You can check the database path in the application by examining the environment variables:

```bash
docker exec fuzeteai-app env | grep DATABASE_PATH
```

### Container Logs

To view container logs:

```bash
# Application logs
docker logs fuzeteai-app

# SQLite container logs
docker logs fuzeteai-sqlite
```
