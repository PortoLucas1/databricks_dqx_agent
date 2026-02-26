# DQX Data Quality Manager

**Fork of [dediggibyte/databricks_dqx_agent](https://github.com/dediggibyte/databricks_dqx_agent).** All credit for this project goes to the original authors.

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Databricks](https://img.shields.io/badge/Databricks-Apps-FF3621.svg)](https://docs.databricks.com/dev-tools/databricks-apps/index.html)
[![DQX](https://img.shields.io/badge/DQX-Data%20Quality-green.svg)](https://databrickslabs.github.io/dqx/)
[![CI/CD Dev](https://github.com/dediggibyte/databricks_dqx_agent/actions/workflows/ci-cd-dev.yml/badge.svg)](https://github.com/dediggibyte/databricks_dqx_agent/actions/workflows/ci-cd-dev.yml)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://dediggibyte.github.io/databricks_dqx_agent/)

**AI-powered data quality rule generation and validation for Databricks**

A Databricks App for generating, validating, and managing data quality rules using AI assistance with [Databricks DQX](https://databrickslabs.github.io/dqx/).

---

## Features

- **AI-Powered Generation** - Generate DQX rules from natural language prompts
- **Rule Validation** - Validate rules against actual data with pass/fail statistics
- **Version Control** - Store rules in Lakebase with full audit history
- **AI Analysis** - Get coverage insights and recommendations from AI
- **OBO Authentication** - Users only see data they have permission to access

---

## Quick Start

```bash
# 1. Clone and configure
git clone https://github.com/dediggibyte/databricks_dqx_agent.git
cd databricks_dqx_agent

# 2. Set configuration via .env (no secrets in repo)
cp .env.example .env
# Edit .env: set DATABRICKS_HOST, SQL_WAREHOUSE_ID, SERVICE_PRINCIPAL_NAME,
# and optionally LAKEBASE_INSTANCE_NAME / LAKEBASE_DATABASE for Step 4 (Save to Lakebase).

# 3. Deploy (script reads .env and passes vars to the bundle)
./scripts/deploy-dev.sh
```

Access: `https://your-workspace.cloud.databricks.com/apps/dqx-rule-generator-dev`

> **Note:** All sensitive and environment-specific values are read from `.env` (or CI secrets). Nothing is hardcoded in `variables.yml`. DAB automatically deploys notebooks and configures permissions.

---

## Architecture

![DQX Architecture](docs/images/architecture.png)

### Authentication Model

| Component | Auth Method | Description |
|-----------|-------------|-------------|
| **Unity Catalog** | User Token (OBO) | Access data with user's permissions |
| **Jobs** | App Service Principal | Trigger generation/validation jobs |
| **Lakebase** | User OAuth | Store rules with user identity; app has **direct connection** via bound database resource |

The Databricks App connects **directly** to Lakebase: when you bind a Lakebase database resource in DAB (`resources/apps.yml`), the platform injects `PGHOST` and `PGPORT` into the app at runtime. The app uses these with the user's OAuth token (no proxy or intermediate service).

---

## Project Structure

```
databricks_dqx_agent/
├── .env.example              # Template for .env; copy to .env and set values (never commit .env)
├── src/                      # Flask app (deployed to Databricks Apps)
│   ├── app/                  # Application code
│   │   ├── routes/           # API endpoints
│   │   └── services/         # Business logic (databricks, ai, lakebase)
│   ├── templates/            # HTML templates
│   └── static/               # CSS and JavaScript
├── notebooks/                # Databricks notebooks (serverless jobs)
├── resources/                # DAB resource definitions (incl. bound Lakebase database)
├── environments/             # Per-environment configs; variables from .env or CI --var
├── scripts/                  # deploy-dev.sh sources .env and runs bundle deploy
├── docs/                     # Documentation (MkDocs)
└── .github/                  # CI/CD workflows
```

---

## Configuration

All sensitive and environment-specific values are **loaded only from `.env`** (local) or from CI secrets passed as `--var` to the bundle. The repo does not commit secrets; `environments/*/variables.yml` holds empty placeholders filled at deploy time.

### Where values come from

- **App runtime (Databricks):** Required IDs (SQL warehouse, job IDs, Lakebase) are injected by DAB via `valueFrom` in `src/app.yaml` from bound resources—no hardcoded IDs in the app.
- **Bundle deploy (local):** `scripts/deploy-dev.sh` sources `.env` and passes `sql_warehouse_id`, `service_principal_name`, and optionally `lakebase_instance_name` / `lakebase_database` as `--var` to `databricks bundle deploy`.
- **Local dev (Flask):** The app loads `.env` from the project root (e.g. when running `python wsgi.py` from `src/`), with `override=False` so Databricks-injected env vars are never overwritten when running inside the platform.

### Required in `.env` (for deploy and/or local dev)

| Variable | Description |
|----------|-------------|
| `SQL_WAREHOUSE_ID` | SQL Warehouse ID for Unity Catalog queries (e.g. `16e13f48f7427e3d`) |
| `SERVICE_PRINCIPAL_NAME` | Service principal ID for app automation / deployment |
| `DATABRICKS_HOST` | Workspace URL (e.g. `https://your-workspace.cloud.databricks.com`); required for local dev |

Job IDs (`DQ_GENERATION_JOB_ID`, `DQ_VALIDATION_JOB_ID`) are **auto-set by DAB** from bound job resources; you do not set them in `.env` for the deployed app.

### Optional in `.env`

| Variable | Description | Default |
|----------|-------------|---------|
| `LAKEBASE_INSTANCE_NAME` | Lakebase instance (first dropdown in Apps UI) | - |
| `LAKEBASE_DATABASE` | Lakebase database name (second dropdown) | `databricks_postgres` |
| `LAKEBASE_HOST` | Only for local dev if not using bound resource | - |
| `MODEL_SERVING_ENDPOINT` | AI model endpoint | `databricks-claude-sonnet-4-5` |
| `DATABRICKS_TOKEN` | PAT for local dev; or use `DATABRICKS_CLIENT_ID` + `DATABRICKS_CLIENT_SECRET` | - |
| `DATABRICKS_TLS_NO_VERIFY` | Set to `true` only for local dev (e.g. corporate proxy); never in production | - |

---

## Local Development

Copy `.env.example` to `.env` and set at least:

```bash
# Required for catalog/schema/table listing and Jobs API
DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
# One of: PAT (DATABRICKS_TOKEN) or OAuth (DATABRICKS_CLIENT_ID + DATABRICKS_CLIENT_SECRET)
DATABRICKS_TOKEN="your-token"

# For deploy and for app (if testing with bundle)
SQL_WAREHOUSE_ID="your-warehouse-id"
SERVICE_PRINCIPAL_NAME="your-service-principal-id"

# Optional: for Step 4 (Save to Lakebase)
# LAKEBASE_INSTANCE_NAME=...
# LAKEBASE_DATABASE=databricks_postgres
```

Then run the app:

```bash
cd src
pip install -r requirements.txt
python wsgi.py
```

The app loads `.env` from the project root with `override=False`, so when running on Databricks the platform-injected variables (e.g. `PGHOST` for Lakebase) are preserved.

---

## Documentation

| Document | Description |
|----------|-------------|
| [Quick Start](docs/runbook.md) | Deployment guide |
| [Configuration](docs/configuration.md) | Environment variables |
| [Authentication](docs/authentication.md) | OBO and security |
| [Architecture](docs/architecture.md) | System design |
| [API Reference](docs/api-reference.md) | REST endpoints |
| [DQX Checks](docs/dqx-checks.md) | Available check functions |
| [CI/CD](docs/ci-cd.md) | GitHub Actions setup |

**Full Documentation:** [https://dediggibyte.github.io/databricks_dqx_agent/](https://dediggibyte.github.io/databricks_dqx_agent/)

---

## CI/CD

| Environment | Trigger | Workflow |
|-------------|---------|----------|
| `dev` | Push to main, PR | `ci-cd-dev.yml` |
| `stage` | Manual | `ci-cd-stage.yml` |
| `prod` | Manual | `ci-cd-prod.yml` |

---

## Resources

- [Databricks DQX Documentation](https://databrickslabs.github.io/dqx/)
- [Databricks Apps Guide](https://docs.databricks.com/dev-tools/databricks-apps/index.html)
- [Databricks Asset Bundles](https://docs.databricks.com/aws/en/dev-tools/bundles/)

---

## License

MIT License - see [LICENSE](LICENSE) for details.
