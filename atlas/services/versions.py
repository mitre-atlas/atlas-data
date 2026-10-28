from __future__ import annotations

from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, make_transient

from atlas import models, schemas
from atlas.constants import ATLAS_COLLECTION_ID
from atlas.db import transactional
from atlas.mappers import versions as version_mapper
from atlas.services.collections import get as get_collection

_CHILD_CLASSES = [
    models.Tactic,
    models.Technique,
    models.Mitigation,
    models.CaseStudy,
    models.Entity,
    models.Software,
    models.Collection,
    models.Matrix,
]


def copy(db: Session, base_version: str, new_version: str) -> dict:
    """Copy all objects from base_version to new_version."""
    for cls in _CHILD_CLASSES:
        for obj in db.query(cls).filter(cls.version == base_version).all():
            db.expunge(obj)
            make_transient(obj)
            obj.version = new_version
            db.add(obj)

    # Copy relationships
    for rel in (
        db.query(models.Relationship)
        .filter(models.Relationship.version == base_version)
        .all()
    ):
        db.add(
            models.Relationship(
                source=rel.source,
                target=rel.target,
                version=new_version,
                relationship_type=rel.relationship_type,
                description=rel.description,
                extra_fields=rel.extra_fields,
            )
        )

    return {
        "base_version": base_version,
        "new_version": new_version,
        "detail": f"Copied all data from version {base_version} to {new_version}.",
    }


def get(db: Session, version: str) -> models.Version | None:
    try:
        return (
            db.query(models.Version).filter(models.Version.version == version).first()
        )
    except OperationalError:
        return None


def get_one(db: Session, version: str) -> models.Version:
    ver = get(db, version)
    if ver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version} not found.",
        )
    return ver


def get_all(db: Session) -> list[schemas.Version]:
    try:
        versions = db.query(models.Version).order_by(models.Version.version.asc()).all()
    except OperationalError:
        return []
    return [version_mapper.to_schema(ver) for ver in versions]


def create(
    db: Session, body: schemas.VersionCreateRequest
) -> schemas.VersionCreateResponse:
    if get(db, body.new_version) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Version {body.new_version} already exists.",
        )

    today = datetime.now(UTC).date()

    with transactional(db):
        ver = models.Version(
            version=body.new_version,
            base_version=body.base_version,
            created_date=today,
            modified_date=today,
            publish_date=body.publish_date,
        )
        db.add(ver)
        db.flush()
        if body.base_version is not None:
            get_one(db, body.base_version)
            if get_collection(db, body.base_version) is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Collection not found in version {body.base_version}.",
                )
            copy(db, body.base_version, body.new_version)
            mode = "copy"
            detail = f"Copied all data from version {body.base_version} to {body.new_version}."
        else:
            assert body.collection is not None
            db_collection = models.Collection(
                id=ATLAS_COLLECTION_ID,
                version=body.new_version,
                name=body.collection.name,
                description=body.collection.description,
                references=[
                    reference.model_dump(mode="json")
                    for reference in body.collection.references
                ],
                created_date=today,
                modified_date=today,
            )
            db.add(db_collection)
            mode = "create"
            detail = (
                f"Created new version {body.new_version} with collection object only."
            )

    return schemas.VersionCreateResponse(
        mode=mode,
        version=version_mapper.to_schema(ver),
        detail=detail,
    )


def update_metadata(
    db: Session, version: str, body: schemas.VersionUpdateRequest
) -> schemas.Version:
    ver = get_one(db, version)
    with transactional(db):
        ver.publish_date = body.publish_date
        ver.modified_date = datetime.now(UTC).date()
    return version_mapper.to_schema(ver)


def delete(db: Session, version: str) -> dict[str, str]:
    ver = get_one(db, version)

    dependent = (
        db.query(models.Version)
        .filter(
            models.Version.base_version == version, models.Version.version != version
        )
        .first()
    )
    if dependent is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Version {version} cannot be deleted because it is the base_version "
                f"for version {dependent.version}."
            ),
        )

    with transactional(db):
        db.query(models.Relationship).filter(
            models.Relationship.version == version
        ).delete(synchronize_session=False)

        for cls in _CHILD_CLASSES:
            db.query(cls).filter(cls.version == version).delete(
                synchronize_session=False
            )

        db.query(models.AtlasObject).filter(
            models.AtlasObject.version == version
        ).delete(synchronize_session=False)

        db.delete(ver)
    return {
        "version": version,
        "detail": f"Deleted version {version} and all associated data.",
    }
