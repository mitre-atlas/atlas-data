from __future__ import annotations

from atlas import models, schemas
from atlas.enums import (
    TechniqueMaturity,
    TechniquePlatformType,
    build_enum_list,
    sort_enum_values,
)


def to_model(
    body: schemas.TechniqueInput | schemas.Technique,
    *,
    technique_id: str,
    version: str,
    maturity: TechniqueMaturity = TechniqueMaturity.FEASIBLE,
) -> models.Technique:
    return models.Technique(
        id=technique_id,
        version=version,
        name=body.name,
        description=body.description,
        references=[ref.model_dump(mode="json") for ref in body.references],
        created_date=body.created_date,
        modified_date=body.modified_date,
        platforms=sort_enum_values(
            [platform.value for platform in body.platforms], TechniquePlatformType
        ),
        attack_reference=(
            body.attack_reference.model_dump(mode="json")
            if body.attack_reference is not None
            else None
        ),
        maturity=maturity,
    )


def update_model(db_obj: models.Technique, body: schemas.TechniqueInput) -> None:
    if "maturity" in body.model_fields_set:
        db_obj.maturity = body.maturity
    db_obj.name = body.name
    db_obj.description = body.description
    db_obj.references = [ref.model_dump(mode="json") for ref in body.references]
    db_obj.created_date = body.created_date
    db_obj.modified_date = body.modified_date
    db_obj.platforms = sort_enum_values(
        [platform.value for platform in body.platforms], TechniquePlatformType
    )
    db_obj.attack_reference = (
        body.attack_reference.model_dump(mode="json")
        if body.attack_reference is not None
        else None
    )


def to_schema(
    db_obj: models.Technique,
) -> schemas.TechniqueResponse:
    tactics = []
    specializes = None
    for rel in db_obj.source_relationships:
        if rel.relationship_type == models.AtlasRelationshipType.ACHIEVES:
            tactics.append(
                schemas.AchievesRelationshipFields(
                    tactic=rel.target,
                    description=rel.description,
                )
            )
        elif rel.relationship_type == models.AtlasRelationshipType.SPECIALIZES:
            specializes = schemas.SpecializesRelationshipFields(
                technique=rel.target,
                description=rel.description,
            )

    attack_reference = (
        schemas.AttackReference(**db_obj.attack_reference)
        if db_obj.attack_reference is not None
        else None
    )

    return schemas.TechniqueResponse(
        id=db_obj.id,
        name=db_obj.name,
        description=db_obj.description,
        references=db_obj.references or [],
        created_date=db_obj.created_date,
        modified_date=db_obj.modified_date,
        platforms=build_enum_list(db_obj.platforms or [], TechniquePlatformType),
        attack_reference=attack_reference,
        maturity=db_obj.maturity,
        tactics=tactics,
        specializes=specializes,
    )


def to_export_schema(db_obj: models.Technique) -> schemas.Technique:
    attack_reference = (
        schemas.AttackReference(**db_obj.attack_reference)
        if db_obj.attack_reference is not None
        else None
    )

    return schemas.Technique(
        id=db_obj.id,
        name=db_obj.name,
        description=db_obj.description,
        references=db_obj.references or [],
        created_date=db_obj.created_date,
        modified_date=db_obj.modified_date,
        platforms=build_enum_list(db_obj.platforms or [], TechniquePlatformType),
        attack_reference=attack_reference,
        maturity=db_obj.maturity,
    )
