from __future__ import annotations

import sqlite3
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, event, pool

import atlas.models  # noqa: F401
from atlas.db.database import Base, DATABASE_URL

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url() -> str:
    return config.get_main_option("sqlalchemy.url") or DATABASE_URL


def run_migrations_offline() -> None:
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    @event.listens_for(connectable, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record) -> None:
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            # SQLite batch migrations rebuild tables referenced by other tables.
            # Disable enforcement before the transaction and validate before commit.
            cursor.execute("PRAGMA foreign_keys=OFF")
            cursor.close()

    with connectable.connect() as connection:
        if connection.dialect.name == "sqlite":
            # Explicit BEGIN also makes DDL transactional with sqlite3's legacy
            # transaction mode. Alembic joins this transaction rather than committing
            # each revision before the integrity check below.
            connection.exec_driver_sql("BEGIN")
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()
            if connection.dialect.name == "sqlite":
                violations = connection.exec_driver_sql(
                    "PRAGMA foreign_key_check"
                ).fetchall()
                if violations:
                    raise RuntimeError(
                        f"Foreign key violations after migration: {violations}"
                    )
        if connection.dialect.name == "sqlite":
            connection.commit()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
