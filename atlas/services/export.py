from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from atlas import mappers, models, schemas, services
from atlas.enums import AtlasRelationshipType


def build(db: Session, version: str) -> schemas.AtlasExport:
    """Build the flat-format AtlasExport from DB for a version."""
    db_collection = services.collections.get(db, version)
    if not db_collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection not found for version {version}.",
        )

    db_matrix = services.matrices.get(db, version)
    if not db_matrix:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Matrix not found for version {version}.",
        )

    tactics = {
        t.id: mappers.tactics.to_export_schema(t)
        for t in sorted(services.tactics.get_all(db, version), key=lambda t: t.id)
    }

    techniques = {
        t.id: mappers.techniques.to_export_schema(t)
        for t in sorted(services.techniques.get_all(db, version), key=lambda t: t.id)
    }

    mitigations = {
        m.id: mappers.mitigations.to_export_schema(m)
        for m in sorted(services.mitigations.get_all(db, version), key=lambda m: m.id)
    }

    case_studies = {
        c.id: mappers.case_studies.to_export_schema(c)
        for c in sorted(services.case_studies.get_all(db, version), key=lambda c: c.id)
    }

    entities = {
        e.id: mappers.entities.to_export_schema(e)
        for e in sorted(services.entities.get_all(db, version), key=lambda e: e.id)
    }

    software = {
        s.id: mappers.software.to_export_schema(s)
        for s in sorted(services.software.get_all(db, version), key=lambda s: s.id)
    }

    # Build relationships dict from the DB
    db_rels = (
        db.query(models.Relationship)
        .filter(models.Relationship.version == version)
        .all()
    )

    relationships: dict[
        str, dict[AtlasRelationshipType, list[schemas.AtlasRelationship]]
    ] = {}

    def _relationship_sort_key(rel: models.Relationship) -> tuple[str, str, int, str]:
        extra = rel.extra_fields or {}
        raw_position = extra.get("position")
        position = raw_position if isinstance(raw_position, int) else None
        if rel.relationship_type == AtlasRelationshipType.SEQUENCES:
            return (
                rel.source,
                rel.relationship_type.value,
                position if position is not None else 2**31 - 1,
                rel.target,
            )
        return (rel.source, rel.relationship_type.value, 0, rel.target)

    for rel in sorted(db_rels, key=_relationship_sort_key):
        extra = rel.extra_fields or {}
        source = rel.source
        rel_type = rel.relationship_type
        if source not in relationships:
            relationships[source] = {}
        if rel_type not in relationships[source]:
            relationships[source][rel_type] = []
        relationships[source][rel_type].append(
            schemas.AtlasRelationship(
                source=rel.source,
                target=rel.target,
                relationship_type=rel.relationship_type,
                description=rel.description,
                tactic=extra.get("tactic"),
                step_id=extra.get("step_id"),
                leads_to=extra.get("leads_to"),
                position=extra.get("position"),
                activity_purpose=extra.get("activity_purpose"),
            )
        )

    format_version = services.format_versions.get_format_version(db)
    if format_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active format version configured.",
        )

    return schemas.AtlasExport(
        format_version=format_version.version,
        collection=mappers.collections.to_export_schema(db_collection),
        matrix=mappers.matrices.to_export_schema(db_matrix),
        tactics=tactics,
        techniques=techniques,
        mitigations=mitigations,
        case_studies=case_studies,
        entities=entities,
        software=software,
        relationships=relationships,
    )
