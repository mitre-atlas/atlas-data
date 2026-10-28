from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from atlas import models, schemas
from atlas.db import safe_flush, transactional
from atlas.enums import AtlasObjectType, AtlasRelationshipType
from atlas.mappers import techniques as technique_mapper
from atlas.services.common import (
    generate_next_id,
    replace_source_relationships,
    require_version,
)


def create(
    db: Session, technique: schemas.TechniqueInput, version: str
) -> models.Technique:
    require_version(db, version)
    sub_of = technique.specializes.technique if technique.specializes else None
    technique_id = generate_next_id(
        db, AtlasObjectType.TECHNIQUE, version, specializes_target=sub_of
    )

    db_technique = technique_mapper.to_model(
        technique,
        technique_id=technique_id,
        version=version,
        maturity=technique.maturity,
    )

    if technique.specializes:
        parent_id = technique.specializes.technique
        parent = get(db, parent_id, version)
        _validate_specializes_relationship(db_parent=parent, db_technique=db_technique)
        assert parent is not None
        _validate_subtechnique_tactics_match_parent(
            db_parent=parent, technique=technique
        )
        rel = models.Relationship(
            source=technique_id,
            target=parent_id,
            version=version,
            relationship_type=models.AtlasRelationshipType.SPECIALIZES,
            description=technique.specializes.description,
        )
        db.add(rel)

    for tactic_rel in technique.tactics:
        rel = models.Relationship(
            source=technique_id,
            target=tactic_rel.tactic,
            version=version,
            relationship_type=models.AtlasRelationshipType.ACHIEVES,
            description=tactic_rel.description,
        )
        db.add(rel)

    with transactional(db):
        db.add(db_technique)
        safe_flush(db)
    db.refresh(db_technique)
    return db_technique


def get(db: Session, technique_id: str, version: str) -> models.Technique | None:
    return (
        db.query(models.Technique)
        .filter(
            models.Technique.id == technique_id,
            models.Technique.version == version,
        )
        .first()
    )


def get_one(db: Session, technique_id: str, version: str) -> models.Technique:
    technique = get(db, technique_id, version)
    if technique is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Technique with id {technique_id} not found in version {version}.",
        )
    return technique


def get_all(db: Session, version: str) -> list[models.Technique]:
    return db.query(models.Technique).filter(models.Technique.version == version).all()


def update(
    db: Session, technique_id: str, version: str, technique: schemas.TechniqueInput
) -> models.Technique:
    db_technique = get_one(db, technique_id, version)

    with transactional(db):
        technique_mapper.update_model(db_technique, technique)

        replace_source_relationships(
            db,
            db_technique,
            models.AtlasRelationshipType.SPECIALIZES,
            [],
        )

        if technique.specializes:
            db_parent = get_one(db, technique.specializes.technique, version)
            _validate_specializes_relationship(
                db_technique=db_technique,
                db_parent=db_parent,
            )
            _validate_subtechnique_tactics_match_parent(
                db_parent=db_parent,
                technique=technique,
            )
            db.add(
                models.Relationship(
                    source=technique_id,
                    target=db_parent.id,
                    version=version,
                    relationship_type=models.AtlasRelationshipType.SPECIALIZES,
                    description=technique.specializes.description,
                )
            )
            _set_subtechnique_tactics_from_parent(
                db,
                db_technique,
                db_parent,
                {rel.tactic: rel.description for rel in technique.tactics},
            )
            safe_flush(db)

        if not db_technique.parent:
            achieves_relationships = [
                models.Relationship(
                    source=db_technique.id,
                    target=rel.tactic,
                    version=db_technique.version,
                    relationship_type=models.AtlasRelationshipType.ACHIEVES,
                    description=rel.description,
                )
                for rel in technique.tactics
            ]
            replace_source_relationships(
                db,
                db_technique,
                models.AtlasRelationshipType.ACHIEVES,
                achieves_relationships,
            )

        for child in db_technique.subtechniques:
            _set_subtechnique_tactics_from_parent(db, child, db_technique)

        safe_flush(db)

    db.refresh(db_technique)
    return db_technique


def delete(db: Session, technique_id: str, version: str):
    db_technique = get_one(db, technique_id, version)

    with transactional(db):
        for child in db_technique.subtechniques:
            db.delete(child)

        db.delete(db_technique)
    return {"detail": f"Technique {technique_id} was deleted successfully."}


def _validate_specializes_relationship(
    db_parent: models.Technique | None,
    db_technique: models.Technique | None = None,
) -> None:
    if db_parent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent technique not found.",
        )

    if db_parent.parent is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invalid specialization: parent technique is already a subtechnique.",
        )

    if db_technique is not None and db_parent.id == db_technique.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Technique cannot specialize itself.",
        )

    if db_technique is not None and db_technique.subtechniques:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Invalid specialization: technique cannot specialize another "
                "technique because it already has subtechniques."
            ),
        )


def _validate_subtechnique_tactics_match_parent(
    db_parent: models.Technique,
    technique: schemas.TechniqueInput,
) -> None:
    requested_ids = {rel.tactic for rel in technique.tactics}
    expected_ids = {
        rel.target
        for rel in db_parent.source_relationships
        if rel.relationship_type == AtlasRelationshipType.ACHIEVES
    }
    if requested_ids != expected_ids:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subtechnique tactics must match parent technique.",
        )


def _set_subtechnique_tactics_from_parent(
    db: Session,
    db_subtechnique: models.Technique,
    db_parent: models.Technique,
    descriptions: dict[str, str | None] | None = None,
) -> None:
    existing_descriptions = {
        rel.target: rel.description
        for rel in db_subtechnique.source_relationships
        if rel.relationship_type == AtlasRelationshipType.ACHIEVES
    }
    achieves_relationships = [
        models.Relationship(
            source=db_subtechnique.id,
            target=rel.target,
            version=db_subtechnique.version,
            relationship_type=models.AtlasRelationshipType.ACHIEVES,
            description=(
                descriptions[rel.target]
                if descriptions is not None and rel.target in descriptions
                else existing_descriptions.get(rel.target)
            ),
        )
        for rel in db_parent.source_relationships
        if rel.relationship_type == AtlasRelationshipType.ACHIEVES
    ]
    replace_source_relationships(
        db,
        db_subtechnique,
        AtlasRelationshipType.ACHIEVES,
        achieves_relationships,
    )
