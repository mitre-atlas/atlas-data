from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from atlas import models, schemas
from atlas.db import transactional
from atlas.enums import AtlasObjectType
from atlas.mappers import mitigations as mitigation_mapper
from atlas.services.common import (
    generate_next_id,
    replace_source_relationships,
    require_version,
)


def create(
    db: Session, mitigation: schemas.MitigationInput, version: str
) -> models.Mitigation:
    require_version(db, version)
    mitigation_id = generate_next_id(db, AtlasObjectType.MITIGATION, version)

    db_mitigation = mitigation_mapper.to_model(
        mitigation,
        mitigation_id=mitigation_id,
        version=version,
    )

    for mitigates_rel in mitigation.mitigates:
        rel = models.Relationship(
            source=mitigation_id,
            target=mitigates_rel.technique,
            version=version,
            relationship_type=models.AtlasRelationshipType.MITIGATES,
            description=mitigates_rel.description,
        )
        db.add(rel)

    with transactional(db):
        db.add(db_mitigation)
    db.refresh(db_mitigation)
    return db_mitigation


def get(db: Session, mitigation_id: str, version: str) -> models.Mitigation | None:
    return (
        db.query(models.Mitigation)
        .filter(
            models.Mitigation.id == mitigation_id,
            models.Mitigation.version == version,
        )
        .first()
    )


def get_one(db: Session, mitigation_id: str, version: str) -> models.Mitigation:
    mitigation = get(db, mitigation_id, version)
    if mitigation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mitigation with id {mitigation_id} not found in version {version}.",
        )
    return mitigation


def get_all(db: Session, version: str) -> list[models.Mitigation]:
    return (
        db.query(models.Mitigation).filter(models.Mitigation.version == version).all()
    )


def update(
    db: Session, mitigation_id: str, version: str, mitigation: schemas.MitigationInput
) -> models.Mitigation:
    db_mitigation = get_one(db, mitigation_id, version)

    with transactional(db):
        mitigation_mapper.update_model(db_mitigation, mitigation)

        mitigates_relationships = [
            models.Relationship(
                source=db_mitigation.id,
                target=rel.technique,
                version=db_mitigation.version,
                relationship_type=models.AtlasRelationshipType.MITIGATES,
                description=rel.description,
            )
            for rel in mitigation.mitigates
        ]
        replace_source_relationships(
            db,
            db_mitigation,
            models.AtlasRelationshipType.MITIGATES,
            mitigates_relationships,
        )

    db.refresh(db_mitigation)
    return db_mitigation


def delete(db: Session, mitigation_id: str, version: str):
    db_mitigation = get_one(db, mitigation_id, version)

    with transactional(db):
        db.delete(db_mitigation)
    return {"detail": f"Mitigation {mitigation_id} was deleted successfully."}
