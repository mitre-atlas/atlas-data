from __future__ import annotations

from atlas import models, schemas
from atlas.enums import (
    AtlasRelationshipType,
    SoftwareCategory,
    build_enum_list,
    sort_enum_values,
)


def to_model(
    body: schemas.SoftwareInput | schemas.Software,
    *,
    software_id: str,
    version: str,
) -> models.Software:
    return models.Software(
        id=software_id,
        version=version,
        name=body.name,
        description=body.description,
        references=[ref.model_dump(mode="json") for ref in body.references],
        created_date=body.created_date,
        modified_date=body.modified_date,
        software_type=body.software_type,
        software_categories=sort_enum_values(
            [category.value for category in body.software_categories], SoftwareCategory
        ),
        aliases=list(body.aliases),
        attack_reference=(
            body.attack_reference.model_dump(mode="json")
            if body.attack_reference is not None
            else None
        ),
    )


def update_model(db_obj: models.Software, body: schemas.SoftwareInput) -> None:
    db_obj.name = body.name
    db_obj.description = body.description
    db_obj.references = [ref.model_dump(mode="json") for ref in body.references]
    db_obj.created_date = body.created_date
    db_obj.modified_date = body.modified_date
    db_obj.software_type = body.software_type
    db_obj.software_categories = sort_enum_values(
        [category.value for category in body.software_categories], SoftwareCategory
    )
    db_obj.aliases = list(body.aliases)
    db_obj.attack_reference = (
        body.attack_reference.model_dump(mode="json")
        if body.attack_reference is not None
        else None
    )


def to_schema(db_obj: models.Software) -> schemas.SoftwareResponse:
    implementations = [
        schemas.ImplementsTechniqueRelationshipFields(
            technique=rel.target,
            description=rel.description,
        )
        for rel in db_obj.source_relationships
        if rel.relationship_type == AtlasRelationshipType.IMPLEMENTS
    ]
    attack_reference = (
        schemas.AttackReference(**db_obj.attack_reference)
        if db_obj.attack_reference is not None
        else None
    )
    return schemas.SoftwareResponse(
        id=db_obj.id,
        name=db_obj.name,
        description=db_obj.description,
        references=db_obj.references or [],
        created_date=db_obj.created_date,
        modified_date=db_obj.modified_date,
        software_type=db_obj.software_type,
        software_categories=build_enum_list(
            db_obj.software_categories or [], SoftwareCategory
        ),
        aliases=db_obj.aliases or [],
        attack_reference=attack_reference,
        implements=implementations,
    )


def to_export_schema(db_obj: models.Software) -> schemas.Software:
    attack_reference = (
        schemas.AttackReference(**db_obj.attack_reference)
        if db_obj.attack_reference is not None
        else None
    )
    return schemas.Software(
        id=db_obj.id,
        name=db_obj.name,
        description=db_obj.description,
        references=db_obj.references or [],
        created_date=db_obj.created_date,
        modified_date=db_obj.modified_date,
        software_type=db_obj.software_type,
        software_categories=build_enum_list(
            db_obj.software_categories or [], SoftwareCategory
        ),
        aliases=db_obj.aliases or [],
        attack_reference=attack_reference,
    )
