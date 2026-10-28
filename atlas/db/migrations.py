from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy.engine import Engine

_ALEMBIC_CONFIG = Path(__file__).resolve().parents[2] / "alembic.ini"


def upgrade_database(engine: Engine) -> None:
    config = Config(_ALEMBIC_CONFIG)
    config.set_main_option(
        "sqlalchemy.url",
        engine.url.render_as_string(hide_password=False).replace("%", "%%"),
    )
    command.upgrade(config, "head")


def ensure_database_current(engine: Engine) -> None:
    config = Config(_ALEMBIC_CONFIG)
    expected_heads = set(ScriptDirectory.from_config(config).get_heads())
    with engine.connect() as connection:
        current_heads = set(MigrationContext.configure(connection).get_current_heads())

    if current_heads != expected_heads:
        current = ", ".join(sorted(current_heads)) or "none"
        expected = ", ".join(sorted(expected_heads))
        raise RuntimeError(
            "Database schema is not current "
            f"(current revision: {current}; expected: {expected}). "
            "Run `uv run alembic upgrade head`."
        )
