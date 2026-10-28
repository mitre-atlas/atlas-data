from __future__ import annotations

from atlas import models, schemas
from atlas.enums import AtlasObjectType, AtlasRelationshipType


def to_model(
    body: schemas.EntityInput | schemas.Entity,
    *,
    entity_id: str,
    version: str,
) -> models.Entity:
    return models.Entity(
        id=entity_id,
        version=version,
        name=body.name,
        description=body.description,
        references=[ref.model_dump(mode="json") for ref in body.references],
        created_date=body.created_date,
        modified_date=body.modified_date,
        entity_type=body.entity_type,
        associated_entities=[
            group.model_dump(mode="json") for group in body.associated_entities
        ],
        attack_reference=(
            body.attack_reference.model_dump(mode="json")
            if body.attack_reference is not None
            else None
        ),
    )


def update_model(db_obj: models.Entity, body: schemas.EntityInput) -> None:
    db_obj.name = body.name
    db_obj.description = body.description
    db_obj.references = [ref.model_dump(mode="json") for ref in body.references]
    db_obj.created_date = body.created_date
    db_obj.modified_date = body.modified_date
    db_obj.entity_type = body.entity_type
    db_obj.associated_entities = [
        group.model_dump(mode="json") for group in body.associated_entities
    ]
    db_obj.attack_reference = (
        body.attack_reference.model_dump(mode="json")
        if body.attack_reference is not None
        else None
    )


def to_schema(db_obj: models.Entity) -> schemas.EntityResponse:
    uses: list[
        schemas.UsesTechniqueRelationshipFields | schemas.UsesSoftwareRelationshipFields
    ] = []
    for rel in db_obj.source_relationships:
        if rel.relationship_type != AtlasRelationshipType.USES:
            continue
        if rel.target_object.object_type == AtlasObjectType.TECHNIQUE:
            extra = rel.extra_fields or {}
            uses.append(
                schemas.UsesTechniqueRelationshipFields(
                    technique=rel.target,
                    activity_purpose=extra.get("activity_purpose"),
                    description=rel.description,
                )
            )
        elif rel.target_object.object_type == AtlasObjectType.SOFTWARE:
            uses.append(
                schemas.UsesSoftwareRelationshipFields(
                    software=rel.target,
                    description=rel.description,
                )
            )

    attack_reference = (
        schemas.AttackReference(**db_obj.attack_reference)
        if db_obj.attack_reference is not None
        else None
    )
    return schemas.EntityResponse(
        id=db_obj.id,
        name=db_obj.name,
        description=db_obj.description,
        references=db_obj.references or [],
        created_date=db_obj.created_date,
        modified_date=db_obj.modified_date,
        entity_type=db_obj.entity_type,
        associated_entities=db_obj.associated_entities or [],
        attack_reference=attack_reference,
        uses=uses,
    )


def to_export_schema(db_obj: models.Entity) -> schemas.Entity:
    attack_reference = (
        schemas.AttackReference(**db_obj.attack_reference)
        if db_obj.attack_reference is not None
        else None
    )
    return schemas.Entity(
        id=db_obj.id,
        name=db_obj.name,
        description=db_obj.description,
        references=db_obj.references or [],
        created_date=db_obj.created_date,
        modified_date=db_obj.modified_date,
        entity_type=db_obj.entity_type,
        associated_entities=db_obj.associated_entities or [],
        attack_reference=attack_reference,
    )
