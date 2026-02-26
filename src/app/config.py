"""
Configuration management for the DQ Rule Generator App.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root first, then cwd (so running from src/ still finds .env).
# Use override=False so Databricks App runtime env (DATABRICKS_HOST, DATABRICKS_CLIENT_ID,
# DATABRICKS_CLIENT_SECRET) is never overwritten by .env, avoiding "Invalid Token" on Jobs API.
_load_env_from = Path(__file__).resolve().parent.parent.parent
if _load_env_from.joinpath(".env").exists():
    load_dotenv(_load_env_from / ".env", override=False)
load_dotenv(override=False)


def _lakebase_database() -> str:
    """Database name for Lakebase. Prefer LAKEBASE_DATABASE; ignore PGDATABASE if it looks like a hostname."""
    explicit = os.getenv("LAKEBASE_DATABASE")
    if explicit:
        return explicit
    pgdb = os.getenv("PGDATABASE")
    if pgdb and ".database." not in pgdb and not pgdb.startswith("instance-"):
        return pgdb
    return "databricks_postgres"


class Config:
    """Application configuration."""

    # Flask
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dq-rule-generator-secret-key")
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    # Databricks Jobs
    DQ_GENERATION_JOB_ID = os.getenv("DQ_GENERATION_JOB_ID")
    DQ_VALIDATION_JOB_ID = os.getenv("DQ_VALIDATION_JOB_ID")

    # Sample Data
    SAMPLE_DATA_LIMIT = int(os.getenv("SAMPLE_DATA_LIMIT", "100"))

    # Lakebase (PostgreSQL). When using bound resource (valueFrom: dqx-lakebase), DAB sets PGHOST, PGPORT.
    # Database name: prefer LAKEBASE_DATABASE; ignore PGDATABASE if it looks like a hostname (platform bug).
    LAKEBASE_HOST = os.getenv("LAKEBASE_HOST") or os.getenv("PGHOST")
    LAKEBASE_DATABASE = _lakebase_database()
    LAKEBASE_PORT = int(os.getenv("LAKEBASE_PORT") or os.getenv("PGPORT", "5432"))

    # AI Model Serving
    MODEL_SERVING_ENDPOINT = os.getenv("MODEL_SERVING_ENDPOINT", "databricks-claude-sonnet-4-5")

    # SQL Warehouse
    SQL_WAREHOUSE_ID = os.getenv("SQL_WAREHOUSE_ID")

    # Databricks SDK (PAT = personal access token for local dev)
    DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
    DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")

    # OAuth Service Principal (alternative to PAT; use client_id + client_secret from SP OAuth secret)
    DATABRICKS_CLIENT_ID = os.getenv("DATABRICKS_CLIENT_ID")
    DATABRICKS_CLIENT_SECRET = os.getenv("DATABRICKS_CLIENT_SECRET")

    # Local dev only: skip SSL cert verification (e.g. corporate proxy with self-signed cert). Never use in production.
    DATABRICKS_TLS_NO_VERIFY = os.getenv("DATABRICKS_TLS_NO_VERIFY", "").lower() in ("1", "true", "yes")

    @classmethod
    def is_lakebase_configured(cls) -> bool:
        """Check if Lakebase is configured."""
        return bool(cls.LAKEBASE_HOST)

    @classmethod
    def is_job_configured(cls) -> bool:
        """Check if the DQ generation job is configured."""
        return bool(cls.DQ_GENERATION_JOB_ID)

    @classmethod
    def is_validation_job_configured(cls) -> bool:
        """Check if the DQ validation job is configured."""
        return bool(cls.DQ_VALIDATION_JOB_ID)
