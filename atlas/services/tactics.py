from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from atlas import models, schemas
from atlas.db import transactional
from atlas.enums import AtlasObjectType
from atlas.mappers import tactics as tactic_mapper
from atlas.services.common import generate_next_id, require_version


def create(db: Session, tactic: schemas.TacticInput, version: str) -> models.Tactic:
    require_version(db, version)
    tactic_id = generate_next_id(db, AtlasObjectType.TACTIC, version)

    db_tactic = tactic_mapper.to_model(tactic, tactic_id=tactic_id, version=version)
    with transactional(db):
        db.add(db_tactic)
    db.refresh(db_tactic)
    return db_tactic


def get(db: Session, tactic_id: str, version: str) -> models.Tactic | None:
    return (
        db.query(models.Tactic)
        .filter(
            models.Tactic.id == tactic_id,
            models.Tactic.version == version,
        )
        .first()
    )


def get_one(db: Session, tactic_id: str, version: str) -> models.Tactic:
    tactic = get(db, tactic_id, version)
    if tactic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tactic with id {tactic_id} not found in version {version}.",
        )
    return tactic


def get_all(db: Session, version: str) -> list[models.Tactic]:
    return db.query(models.Tactic).filter(models.Tactic.version == version).all()


def update(
    db: Session, tactic_id: str, version: str, tactic: schemas.TacticInput
) -> models.Tactic:
    db_tactic = get_one(db, tactic_id, version)

    with transactional(db):
        tactic_mapper.update_model(db_tactic, tactic)
    db.refresh(db_tactic)
    return db_tactic


def delete(db: Session, tactic_id: str, version: str):
    db_tactic = get_one(db, tactic_id, version)

    with transactional(db):
        db.delete(db_tactic)
    return {"detail": f"Tactic {tactic_id} was deleted successfully."}
