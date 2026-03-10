# ETLCopyData — CLAUDE.md

## Project Overview
ETL pipeline that migrates data from Excel/CSV source files into a Microsoft SQL Server database.
Exposes a Flask REST API for streaming inserts, batch migrations, backups, restores, and reporting.
Includes a dark-themed web dashboard UI served by the same Flask app.

---

## Project Structure

```
ETLCopyData/
├── CLAUDE.md                          # This file
├── Dockerfile                         # App image (python:3.12-slim-bookworm + ODBC Driver 18)
├── docker-compose.yml                 # Orchestrates app + SQL Server 2022 containers
├── .env.example                       # Template for environment variables (copy to .env)
├── .env                               # Local credentials — git-ignored, never commit
├── requirements.txt                   # Python dependencies
│
├── development/                       # Application source code (WORKDIR inside container)
│   ├── api_service.py                 # Flask app — all HTTP routes + entry point
│   ├── connections.py                 # SQLAlchemy engine factory with connection pooling
│   ├── migratedata.py                 # Core ETL logic: batch/streaming load, query helpers
│   ├── process_data.py                # Data cleaning, type casting, null handling
│   ├── backups.py                     # Avro backup and restore logic
│   ├── queries.py                     # SQL query strings (hired by quarter, above mean)
│   ├── templates/
│   │   └── index.html                 # Single-page dashboard UI (Bootstrap 5 + vanilla JS)
│   └── static/
│       └── js/
│           └── app.js                 # Frontend logic — API calls, table rendering, search
│
├── data/                              # Source data files (mounted into container)
│   ├── departments.xlsx
│   ├── jobs.xlsx
│   ├── hired_employees.xlsx
│   └── nulls/                         # Rejected rows saved here during migration
│       ├── batch/                     # Nulls from batch migrations
│       └── streaming/                 # Nulls from streaming inserts
│
├── backups/                           # Avro backup files (git-ignored)
│
├── docker/
│   └── mssql-entrypoint.sh            # Waits for SQL Server readiness, runs DDL init script
│
├── Queries/
│   └── createtable.sql                # DDL — creates migration DB, stage schema, all tables
│
└── testing/
    └── test_process_data.py           # pytest test suite (16 tests)
```

---

## Architecture

```
Browser → http://localhost:5001
              │
              ▼
        Flask (api_service.py)
        ├── GET  /                  → serves dashboard UI
        ├── GET  /table/<table>     → fetch table rows as JSON
        ├── POST /test              → health check
        ├── POST /insert/<table>    → streaming insert (max 1000 rows)
        ├── POST /fullmigrate       → batch load all source files
        ├── POST /backup/<table>    → export table to Avro
        ├── POST /restore/<table>   → restore table from Avro
        └── GET  /getNumHired       → quarterly hiring pivot report
              │
              ▼ SQLAlchemy + pyodbc + ODBC Driver 18
        SQL Server 2022 (localhost:1433)
        └── migration.stage
            ├── departments
            ├── jobs
            └── hired_employees
```

---

## Key Design Decisions

- **ODBC Driver 18** — only version with ARM64 (Apple Silicon) support on Debian 12
- **`TrustServerCertificate=yes`** — required for self-signed cert used by SQL Server in Docker
- **FK-safe load order** — `departments → jobs → hired_employees` (enforced by `LOAD_ORDER` constant)
- **DELETE before load** — uses `DELETE` in reverse FK order instead of `TRUNCATE` (SQL Server blocks TRUNCATE on referenced tables)
- **Environment variables** — all credentials and paths read from `.env`; falls back to `credentials.py` if present
- **Table whitelist** — API validates `<table>` against `ALLOWED_TABLES` set to prevent injection
- **Port 5001** — host port mapped to 5000 inside container (macOS AirPlay occupies 5000)

---

## Environment Variables (.env)

| Variable | Default | Description |
|---|---|---|
| `SA_PASSWORD` | — | SQL Server SA password (must meet complexity rules) |
| `DB_USER` | `sa` | Database login |
| `DB_PWD` | — | Database password |
| `DB_NAME` | `migration` | Database name |
| `DB_SERVER` | `db` | Hostname (Docker service name) |
| `DB_SCHEMA` | `stage` | SQL schema |
| `MAX_ROWS` | `1000` | Max rows per streaming insert |
| `FLASK_DEBUG` | `false` | Enable Flask debug mode |
| `DATA_PATH` | `/app/data` | Source files directory |
| `BACKUP_PATH` | `/app/backups` | Avro backups directory |

---

## Running the Project

```bash
# 1. Copy and fill credentials
cp .env.example .env

# 2. Start everything
docker compose up --build

# 3. Open the dashboard
open http://localhost:5001
```

### Useful commands

```bash
docker compose up --build -d       # Start in background
docker compose start db            # Restart db if it went down
docker compose ps                  # Check container status
docker compose logs app            # App logs
docker compose logs db             # SQL Server logs
docker compose down                # Stop all containers
docker compose down -v             # Stop + delete DB volume (full reset)
```

### Database connection (DBeaver / DataGrip)

| Field | Value |
|---|---|
| Server | `localhost` |
| Port | `1433` |
| Database | `migration` |
| Auth | SQL Server Auth |
| Username | `sa` |
| Password | value from `.env` |
| Trust server certificate | `ON` |

---

## Running Tests

```bash
# Using the project virtual environment
/Users/victormoreno/Desktop/study/cloude/enviroments/claude_env/bin/python \
  -m pytest testing/ -v
```

---

## Database Schema

```sql
migration.stage.departments   (id PK, department)
migration.stage.jobs          (id PK, job)
migration.stage.hired_employees (
    id PK,
    name,
    DATETIME VARCHAR(30),
    department_id FK → departments,
    job_id        FK → jobs
)
```

---

## Branches

| Branch | Purpose |
|---|---|
| `master` | Production-ready code |
| `develop` | Active development — PRs merge here first |

CI/CD runs `pytest testing/` on every pull request to `master`.
