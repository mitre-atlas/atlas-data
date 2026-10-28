from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from atlas import models, schemas
from atlas.db import safe_flush, transactional
from atlas.enums import AtlasObjectType
from atlas.mappers import case_studies as case_study_mapper
from atlas.services.common import (
    generate_next_id,
    replace_source_relationships,
    require_version,
    validate_relationship_types,
)


def create(
    db: Session, case_study: schemas.CaseStudyInput, version: str
) -> models.CaseStudy:
    require_version(db, version)
    case_study_id = generate_next_id(db, AtlasObjectType.CASE_STUDY, version)

    db_case_study = case_study_mapper.to_model(
        case_study,
        case_study_id=case_study_id,
        version=version,
    )

    with transactional(db):
        db.add(db_case_study)
        safe_flush(db)
        db.add_all(_employs_relationships(db_case_study, case_study))
        db.add_all(_attributed_to_relationships(db_case_study, case_study))
        db.add_all(_reported_by_relationships(db_case_study, case_study))
        db.add_all(_uses_software_relationships(db_case_study, case_study))
        safe_flush(db)
    return db_case_study


def get(db: Session, case_study_id: str, version: str) -> models.CaseStudy | None:
    return (
        db.query(models.CaseStudy)
        .filter(
            models.CaseStudy.id == case_study_id,
            models.CaseStudy.version == version,
        )
        .first()
    )


def get_one(db: Session, case_study_id: str, version: str) -> models.CaseStudy:
    case_study = get(db, case_study_id, version)
    if case_study is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case study with id {case_study_id} not found in version {version}.",
        )
    return case_study


def get_all(db: Session, version: str) -> list[models.CaseStudy]:
    return db.query(models.CaseStudy).filter(models.CaseStudy.version == version).all()


def update(
    db: Session,
    case_study_id: str,
    version: str,
    case_study: schemas.CaseStudyInput,
) -> models.CaseStudy:
    db_case_study = get_one(db, case_study_id, version)

    with transactional(db):
        case_study_mapper.update_model(db_case_study, case_study)

        replace_source_relationships(
            db,
            db_case_study,
            models.AtlasRelationshipType.EMPLOYS,
            _employs_relationships(db_case_study, case_study),
        )
        replace_source_relationships(
            db,
            db_case_study,
            models.AtlasRelationshipType.ATTRIBUTED_TO,
            _attributed_to_relationships(db_case_study, case_study),
        )
        replace_source_relationships(
            db,
            db_case_study,
            models.AtlasRelationshipType.REPORTED_BY,
            _reported_by_relationships(db_case_study, case_study),
        )
        replace_source_relationships(
            db,
            db_case_study,
            models.AtlasRelationshipType.USES,
            _uses_software_relationships(db_case_study, case_study),
        )

        safe_flush(db)

    db.refresh(db_case_study)
    return db_case_study


def delete(db: Session, case_study_id: str, version: str):
    db_case_study = get_one(db, case_study_id, version)

    with transactional(db):
        db.delete(db_case_study)
    return {"detail": f"Case study {case_study_id} was deleted successfully."}


def _uses_software_relationships(
    db_case_study: models.CaseStudy,
    case_study: schemas.CaseStudyInput,
) -> list[models.Relationship]:
    return [
        models.Relationship(
            source=db_case_study.id,
            target=use.software,
            version=db_case_study.version,
            relationship_type=models.AtlasRelationshipType.USES,
            description=use.description,
        )
        for use in case_study.uses_software
    ]


def _employs_relationships(
    db_case_study: models.CaseStudy,
    case_study: schemas.CaseStudyInput,
) -> list[models.Relationship]:
    return [
        models.Relationship(
            source=db_case_study.id,
            target=step.technique,
            version=db_case_study.version,
            relationship_type=models.AtlasRelationshipType.EMPLOYS,
            description=step.description,
            extra_fields={
                "tactic": step.tactic,
                "step_id": step.step_id,
                "leads_to": step.leads_to,
            },
        )
        for step in case_study.attack_chain
    ]


def _attributed_to_relationships(
    db_case_study: models.CaseStudy,
    case_study: schemas.CaseStudyInput,
) -> list[models.Relationship]:
    relationships = []
    for attribution in case_study.attributed_to:
        extra_fields = {"activity_purpose": attribution.activity_purpose.value}
        validate_relationship_types(
            AtlasObjectType.CASE_STUDY,
            AtlasObjectType.ENTITY,
            models.AtlasRelationshipType.ATTRIBUTED_TO,
            extra_fields,
        )
        relationships.append(
            models.Relationship(
                source=db_case_study.id,
                target=attribution.entity,
                version=db_case_study.version,
                relationship_type=models.AtlasRelationshipType.ATTRIBUTED_TO,
                description=attribution.description,
                extra_fields=extra_fields,
            )
        )
    return relationships


def _reported_by_relationships(
    db_case_study: models.CaseStudy,
    case_study: schemas.CaseStudyInput,
) -> list[models.Relationship]:
    return [
        models.Relationship(
            source=db_case_study.id,
            target=reporting.entity,
            version=db_case_study.version,
            relationship_type=models.AtlasRelationshipType.REPORTED_BY,
            description=reporting.description,
        )
        for reporting in case_study.reported_by
    ]
