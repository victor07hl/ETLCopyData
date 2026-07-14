# ETLCopyData

An ETL pipeline that migrates data from Excel/CSV source files into a Microsoft SQL Server database, with a Flask REST API for streaming inserts, batch migrations, backups, restores, and reporting — plus a dark-themed web dashboard to drive it all.

## What it does

- **Batch migration** — loads `departments.xlsx`, `jobs.xlsx`, and `hired_employees.xlsx` into SQL Server in FK-safe order (departments → jobs → hired_employees).
- **Streaming inserts** — accepts batches of up to 1,000 rows via the API for incremental loads.
- **Backups & restores** — exports/imports tables as Avro files.
- **Reporting** — quarterly hiring pivot report endpoint.
- **Dashboard UI** — a single-page Bootstrap dashboard (served by the same Flask app) to trigger migrations, browse tables, and run reports without touching the API directly.

## Stack

- **App**: Python 3.12, Flask, SQLAlchemy + pyodbc (ODBC Driver 18)
- **Database**: SQL Server 2022
- **Infra**: Docker Compose (app + db containers)

## Quick start

```bash
# 1. Copy and fill in credentials
cp .env.example .env

# 2. Start everything
docker compose up --build

# 3. Open the dashboard
open http://localhost:5001
```

Configuration is driven entirely by environment variables in `.env` (DB credentials, schema, paths, max rows per streaming insert, etc.) — see `.env.example` for the full list.

## Testing

```bash
/Users/victormoreno/Desktop/study/cloude/enviroments/claude_env/bin/python -m pytest testing/ -v
```

CI runs the full `pytest testing/` suite automatically on every pull request to `master`.

## More details

For the full project structure, architecture diagram, API route reference, environment variable table, and database schema, see [`CLAUDE.md`](CLAUDE.md).

## Branches

| Branch | Purpose |
|---|---|
| `master` | Production-ready code |
| `develop` | Active development — PRs merge here first |
