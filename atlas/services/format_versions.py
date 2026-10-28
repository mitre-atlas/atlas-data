from __future__ import annotations

import re
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from atlas import models
from atlas.constants import (
    ATLAS_FORMAT_VERSION,
    ATLAS_MINIMUM_FORMAT_VERSION,
    ATLAS_SUPPORTED_FORMAT_MAJOR,
)

ATLAS_FORMAT_VERSION_ROW_ID = 1
_NUMERIC_SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def parse_format_version(version: str) -> tuple[int, int, int]:
    match = _NUMERIC_SEMVER.fullmatch(version)
    if match is None:
        raise ValueError(f"Invalid numeric format version: {version}")
    return tuple(int(part) for part in match.groups())


def is_format_version_supported(version: str) -> bool:
    try:
        parsed = parse_format_version(version)
    except ValueError:
        return False

    minimum = parse_format_version(ATLAS_MINIMUM_FORMAT_VERSION)
    current = parse_format_version(ATLAS_FORMAT_VERSION)
    return parsed[0] == ATLAS_SUPPORTED_FORMAT_MAJOR and minimum <= parsed <= current


def get_format_version(db: Session) -> models.FormatVersion | None:
    return db.get(models.FormatVersion, ATLAS_FORMAT_VERSION_ROW_ID)


def init_format_version(db: Session, version: str) -> models.FormatVersion:
    today = datetime.now(UTC).date()
    db_obj = get_format_version(db)
    if db_obj is None:
        db_obj = models.FormatVersion(
            id=ATLAS_FORMAT_VERSION_ROW_ID,
            version=version,
            created_date=today,
            modified_date=today,
        )
        db.add(db_obj)
        db.flush()
        return db_obj

    db_obj.version = version
    db_obj.modified_date = today
    db.flush()
    return db_obj


def ensure_format_version_set(
    db: Session, default_version: str = ATLAS_FORMAT_VERSION
) -> models.FormatVersion:
    format_version = get_format_version(db)
    if format_version is None:
        return init_format_version(db, default_version)
    return format_version


def assert_format_version_supported(
    db: Session, incoming_version: str
) -> models.FormatVersion:
    format_version = ensure_format_version_set(db)
    if not is_format_version_supported(incoming_version):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Unsupported format-version {incoming_version}; expected a version "
                f"from {ATLAS_MINIMUM_FORMAT_VERSION} through {ATLAS_FORMAT_VERSION}."
            ),
        )
    return format_version
