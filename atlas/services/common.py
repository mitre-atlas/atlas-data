from __future__ import annotations

import re

from fastapi import HTTPException, status
from sqlalchemy import Integer as SQLInteger
from sqlalchemy import cast, func
from sqlalchemy.orm import Session

from atlas import models
from atlas.enums import (
    AtlasObjectType,
    AtlasRelationshipType,
)

_ID_PREFIXES: dict[AtlasObjectType, tuple[str, int]] = {
    AtlasObjectType.TACTIC: ("AML.TA", 4),
    AtlasObjectType.TECHNIQUE: ("AML.T", 4),
    AtlasObjectType.MITIGATION: ("AML.M", 4),
    AtlasObjectType.CASE_STUDY: ("AML.CS", 4),
    AtlasObjectType.ENTITY: ("AML.E", 4),
    AtlasObjectType.SOFTWARE: ("AML.S", 4),
}

_SUBTECHNIQUE_RE = re.compile(r"^AML\.T(\d{4})$")

_ALLOWED_ENDPOINT_TYPES = {
    AtlasRelationshipType.SEQUENCES: {
        (AtlasObjectType.MATRIX, AtlasObjectType.TACTIC),
    },
    AtlasRelationshipType.ACHIEVES: {
        (AtlasObjectType.TECHNIQUE, AtlasObjectType.TACTIC),
    },
    AtlasRelationshipType.SPECIALIZES: {
        (AtlasObjectType.TECHNIQUE, AtlasObjectType.TECHNIQUE),
    },
    AtlasRelationshipType.MITIGATES: {
        (AtlasObjectType.MITIGATION, AtlasObjectType.TECHNIQUE),
    },
    AtlasRelationshipType.EMPLOYS: {
        (AtlasObjectType.CASE_STUDY, AtlasObjectType.TECHNIQUE),
    },
    AtlasRelationshipType.ATTRIBUTED_TO: {
        (AtlasObjectType.CASE_STUDY, AtlasObjectType.ENTITY),
    },
    AtlasRelationshipType.REPORTED_BY: {
        (AtlasObjectType.CASE_STUDY, AtlasObjectType.ENTITY),
    },
    AtlasRelationshipType.USES: {
        (AtlasObjectType.CASE_STUDY, AtlasObjectType.SOFTWARE),
        (AtlasObjectType.ENTITY, AtlasObjectType.TECHNIQUE),
        (AtlasObjectType.ENTITY, AtlasObjectType.SOFTWARE),
    },
    AtlasRelationshipType.IMPLEMENTS: {
        (AtlasObjectType.SOFTWARE, AtlasObjectType.TECHNIQUE),
    },
}

_ALLOWED_METADATA_FIELDS = {
    (
        AtlasRelationshipType.SEQUENCES,
        AtlasObjectType.MATRIX,
        AtlasObjectType.TACTIC,
    ): {"position"},
    (
        AtlasRelationshipType.EMPLOYS,
        AtlasObjectType.CASE_STUDY,
        AtlasObjectType.TECHNIQUE,
    ): {"tactic", "step_id", "leads_to"},
    (
        AtlasRelationshipType.ATTRIBUTED_TO,
        AtlasObjectType.CASE_STUDY,
        AtlasObjectType.ENTITY,
    ): {"activity_purpose"},
    (
        AtlasRelationshipType.USES,
        AtlasObjectType.ENTITY,
        AtlasObjectType.TECHNIQUE,
    ): {"activity_purpose"},
}

_REQUIRED_METADATA_FIELDS = {
    (
        AtlasRelationshipType.ATTRIBUTED_TO,
        AtlasObjectType.CASE_STUDY,
        AtlasObjectType.ENTITY,
    ): {"activity_purpose"},
    (
        AtlasRelationshipType.USES,
        AtlasObjectType.ENTITY,
        AtlasObjectType.TECHNIQUE,
    ): {"activity_purpose"},
}


def validate_relationship_types(
    source_type: AtlasObjectType,
    target_type: AtlasObjectType,
    relationship_type: AtlasRelationshipType,
    extra_fields: dict | None = None,
) -> None:
    endpoint_types = (source_type, target_type)
    if endpoint_types not in _ALLOWED_ENDPOINT_TYPES[relationship_type]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Invalid {relationship_type.value} relationship from "
                f"{source_type.value} to {target_type.value}."
            ),
        )

    metadata_key = (relationship_type, source_type, target_type)
    present_fields = set(extra_fields or {})
    unexpected_fields = present_fields - _ALLOWED_METADATA_FIELDS.get(
        metadata_key, set()
    )
    if unexpected_fields:
        fields = ", ".join(sorted(unexpected_fields))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"Relationship type {relationship_type.value} does not allow "
                f"metadata fields: {fields}."
            ),
        )

    missing_fields = _REQUIRED_METADATA_FIELDS.get(metadata_key, set()) - present_fields
    if missing_fields:
        fields = ", ".join(sorted(missing_fields))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"Relationship type {relationship_type.value} requires metadata "
                f"fields: {fields}."
            ),
        )


def generate_next_id(
    db: Session,
    object_type: AtlasObjectType,
    version: str,
    *,
    specializes_target: str | None = None,
) -> str:
    """Generate the next auto-incremented ID for an object type within a version."""
    prefix, width = _ID_PREFIXES[object_type]

    if object_type == AtlasObjectType.TECHNIQUE and specializes_target:
        # Generate subtechnique ID: AML.T{parent}.{NNN}
        match = _SUBTECHNIQUE_RE.match(specializes_target)
        if not match:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid parent technique ID: {specializes_target}",
            )
        parent_num = match.group(1)
        sub_prefix = f"AML.T{parent_num}."
        max_num = (
            db.query(
                func.max(
                    cast(
                        func.substr(models.Technique.id, len(sub_prefix) + 1),
                        SQLInteger,
                    )
                )
            )
            .filter(
                models.Technique.version == version,
                models.Technique.id.like(f"{sub_prefix}%"),
            )
            .scalar()
        )
        next_num = 0 if max_num is None else max_num + 1
        return f"AML.T{parent_num}.{next_num:03d}"

    max_num = (
        db.query(
            func.max(
                cast(
                    func.substr(models.AtlasObject.id, len(prefix) + 1),
                    SQLInteger,
                )
            )
        )
        .filter(
            models.AtlasObject.object_type == object_type,
            models.AtlasObject.version == version,
            models.AtlasObject.id.like(f"{prefix}%"),
        )
        .scalar()
    )
    max_num = max_num or 0

    return f"{prefix}{max_num + 1:0{width}d}"


def require_version(db: Session, version: str) -> models.Version:
    db_version = db.get(models.Version, version)
    if db_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version} not found.",
        )
    return db_version


def replace_source_relationships(
    db: Session,
    db_obj: models.AtlasObject,
    relationship_type: AtlasRelationshipType,
    new_relationships: list[models.Relationship],
) -> None:
    db_obj.source_relationships = [
        rel
        for rel in db_obj.source_relationships
        if rel.relationship_type != relationship_type
    ]
    db.flush()
    db_obj.source_relationships.extend(new_relationships)
