from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from atlas import models, schemas
from atlas.db import safe_flush, transactional
from atlas.enums import AtlasObjectType, AtlasRelationshipType
from atlas.mappers import software as software_mapper
from atlas.services.common import (
    generate_next_id,
    replace_source_relationships,
    require_version,
    validate_relationship_types,
)


def create(
    db: Session, software: schemas.SoftwareInput, version: str
) -> models.Software:
    require_version(db, version)
    software_id = generate_next_id(db, AtlasObjectType.SOFTWARE, version)
    db_software = software_mapper.to_model(
        software,
        software_id=software_id,
        version=version,
    )

    with transactional(db):
        db.add(db_software)
        safe_flush(db)
        db.add_all(_implements_relationships(db_software, software.implements))
        safe_flush(db)

    db.refresh(db_software)
    return db_software


def get(db: Session, software_id: str, version: str) -> models.Software | None:
    return (
        db.query(models.Software)
        .filter(
            models.Software.id == software_id,
            models.Software.version == version,
        )
        .first()
    )


def get_one(db: Session, software_id: str, version: str) -> models.Software:
    software = get(db, software_id, version)
    if software is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Software with id {software_id} not found in version {version}.",
        )
    return software


def get_all(db: Session, version: str) -> list[models.Software]:
    return db.query(models.Software).filter(models.Software.version == version).all()


def update(
    db: Session,
    software_id: str,
    version: str,
    software: schemas.SoftwareInput,
) -> models.Software:
    db_software = get_one(db, software_id, version)

    with transactional(db):
        software_mapper.update_model(db_software, software)
        implements_relationships = _implements_relationships(
            db_software, software.implements
        )
        replace_source_relationships(
            db,
            db_software,
            AtlasRelationshipType.IMPLEMENTS,
            implements_relationships,
        )
        safe_flush(db)

    db.refresh(db_software)
    return db_software


def delete(db: Session, software_id: str, version: str):
    db_software = get_one(db, software_id, version)
    with transactional(db):
        db.delete(db_software)
    return {"detail": f"Software {software_id} was deleted successfully."}


def _implements_relationships(
    db_software: models.Software,
    implementations: list[schemas.ImplementsTechniqueRelationshipFields],
) -> list[models.Relationship]:
    relationships = []
    for implementation in implementations:
        validate_relationship_types(
            AtlasObjectType.SOFTWARE,
            AtlasObjectType.TECHNIQUE,
            AtlasRelationshipType.IMPLEMENTS,
        )
        relationships.append(
            models.Relationship(
                source=db_software.id,
                target=implementation.technique,
                version=db_software.version,
                relationship_type=AtlasRelationshipType.IMPLEMENTS,
                description=implementation.description,
            )
        )
    return relationships
