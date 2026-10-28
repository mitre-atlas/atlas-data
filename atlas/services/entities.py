from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from atlas import models, schemas
from atlas.db import safe_flush, transactional
from atlas.enums import AtlasObjectType, AtlasRelationshipType
from atlas.mappers import entities as entity_mapper
from atlas.services.common import (
    generate_next_id,
    replace_source_relationships,
    require_version,
    validate_relationship_types,
)


def create(db: Session, entity: schemas.EntityInput, version: str) -> models.Entity:
    require_version(db, version)
    entity_id = generate_next_id(db, AtlasObjectType.ENTITY, version)
    db_entity = entity_mapper.to_model(entity, entity_id=entity_id, version=version)

    with transactional(db):
        db.add(db_entity)
        safe_flush(db)
        db.add_all(_uses_relationships(db_entity, entity.uses))
        safe_flush(db)

    db.refresh(db_entity)
    return db_entity


def get(db: Session, entity_id: str, version: str) -> models.Entity | None:
    return (
        db.query(models.Entity)
        .filter(
            models.Entity.id == entity_id,
            models.Entity.version == version,
        )
        .first()
    )


def get_one(db: Session, entity_id: str, version: str) -> models.Entity:
    entity = get(db, entity_id, version)
    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entity with id {entity_id} not found in version {version}.",
        )
    return entity


def get_all(db: Session, version: str) -> list[models.Entity]:
    return db.query(models.Entity).filter(models.Entity.version == version).all()


def update(
    db: Session,
    entity_id: str,
    version: str,
    entity: schemas.EntityInput,
) -> models.Entity:
    db_entity = get_one(db, entity_id, version)

    with transactional(db):
        entity_mapper.update_model(db_entity, entity)
        uses_relationships = _uses_relationships(db_entity, entity.uses)
        replace_source_relationships(
            db,
            db_entity,
            AtlasRelationshipType.USES,
            uses_relationships,
        )
        safe_flush(db)

    db.refresh(db_entity)
    return db_entity


def delete(db: Session, entity_id: str, version: str):
    db_entity = get_one(db, entity_id, version)

    with transactional(db):
        db.delete(db_entity)
    return {"detail": f"Entity {entity_id} was deleted successfully."}


def _uses_relationships(
    db_entity: models.Entity,
    uses: list[
        schemas.UsesTechniqueRelationshipFields | schemas.UsesSoftwareRelationshipFields
    ],
) -> list[models.Relationship]:
    relationships = []
    for use in uses:
        if isinstance(use, schemas.UsesTechniqueRelationshipFields):
            target_id = use.technique
            target_type = AtlasObjectType.TECHNIQUE
            extra_fields = {"activity_purpose": use.activity_purpose.value}
        else:
            target_id = use.software
            target_type = AtlasObjectType.SOFTWARE
            extra_fields = None
        validate_relationship_types(
            AtlasObjectType.ENTITY,
            target_type,
            AtlasRelationshipType.USES,
            extra_fields,
        )
        relationships.append(
            models.Relationship(
                source=db_entity.id,
                target=target_id,
                version=db_entity.version,
                relationship_type=AtlasRelationshipType.USES,
                description=use.description,
                extra_fields=extra_fields,
            )
        )
    return relationships
