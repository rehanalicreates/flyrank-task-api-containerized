"""
App configuration, loaded from environment variables (via .env locally).

Why this file exists: hardcoding a database password/URL directly in code
means it ends up in Git history forever, visible to anyone with repo access.
Instead, the actual secret lives in `.env` (gitignored, never committed),
and this file just knows the *name* of the setting to look for.

`.env.example` (committed) documents which variables are needed, with fake
placeholder values, so anyone cloning the repo knows what to fill in.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/flyrank_tasks"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
