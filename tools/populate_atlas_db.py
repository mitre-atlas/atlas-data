"""Populate the ATLAS database from a YAML export."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from atlas import mappers, models, schemas
from atlas.db import SessionLocal, engine, upgrade_database
from atlas.enums import AtlasObjectType, AtlasRelationshipType
from atlas.services.common import (
    validate_relationship_types,
)
from atlas.services.format_versions import (
    assert_format_version_supported,
    ensure_format_version_set,
)

_VERSION_CHILDREN = [
    models.CaseStudy,
    models.Collection,
    models.Matrix,
    models.Mitigation,
    models.Entity,
    models.Software,
    models.Tactic,
    models.Technique,
]


def load_yaml_export(yaml_path: Path) -> schemas.AtlasExport:
    print(f"Loading {yaml_path}...")
    with yaml_path.open("r") as f:
        data = yaml.safe_load(f)
    return schemas.AtlasExport.model_validate(data)


def get_existing_version(db: Session, version: str) -> models.Version | None:
    return db.query(models.Version).filter(models.Version.version == version).first()


def delete_version_data(db: Session, version: str) -> None:
    db.query(models.Relationship).filter(
        models.Relationship.version == version
    ).delete()
    for model in _VERSION_CHILDREN:
        db.query(model).filter(model.version == version).delete()
    db.query(models.AtlasObject).filter(models.AtlasObject.version == version).delete()
    db.query(models.Version).filter(models.Version.version == version).delete()


def insert_collection(db: Session, export: schemas.AtlasExport, version: str) -> None:
    db_collection = models.Collection(
        id=export.collection.id,
        version=version,
        name=export.collection.name,
        description=export.collection.description,
        references=[
            ref.model_dump(mode="json") for ref in export.collection.references
        ],
        created_date=export.collection.created_date,
        modified_date=export.collection.modified_date,
    )
    db.add(db_collection)
    db.flush()


def insert_version_row(db: Session, version: str) -> None:
    db.add(models.Version(version=version, base_version=None))
    db.flush()


def insert_matrix(db: Session, export: schemas.AtlasExport, version: str) -> None:
    db_matrix = models.Matrix(
        id=export.matrix.id,
        version=version,
        name=export.matrix.name,
        description=export.matrix.description,
        references=[ref.model_dump(mode="json") for ref in export.matrix.references],
        created_date=export.matrix.created_date,
        modified_date=export.matrix.modified_date,
    )
    db.add(db_matrix)
    db.flush()


def insert_tactics(db: Session, export: schemas.AtlasExport, version: str) -> None:
    for tactic in export.tactics.values():
        db_tactic = mappers.tactics.to_model(
            tactic,
            tactic_id=tactic.id,
            version=version,
        )
        db.add(db_tactic)
    db.flush()


def insert_techniques(db: Session, export: schemas.AtlasExport, version: str) -> None:
    for technique in export.techniques.values():
        db_technique = mappers.techniques.to_model(
            technique,
            technique_id=technique.id,
            version=version,
            maturity=technique.maturity,
        )
        db.add(db_technique)
    db.flush()


def insert_mitigations(db: Session, export: schemas.AtlasExport, version: str) -> None:
    for mitigation in export.mitigations.values():
        db_mitigation = mappers.mitigations.to_model(
            mitigation,
            mitigation_id=mitigation.id,
            version=version,
        )
        db.add(db_mitigation)
    db.flush()


def insert_entities(db: Session, export: schemas.AtlasExport, version: str) -> None:
    for entity in export.entities.values():
        db.add(
            mappers.entities.to_model(
                entity,
                entity_id=entity.id,
                version=version,
            )
        )
    db.flush()


def insert_software(db: Session, export: schemas.AtlasExport, version: str) -> None:
    for software in export.software.values():
        db.add(
            mappers.software.to_model(
                software,
                software_id=software.id,
                version=version,
            )
        )
    db.flush()


def insert_case_studies(db: Session, export: schemas.AtlasExport, version: str) -> None:
    for case_study in export.case_studies.values():
        db_case_study = mappers.case_studies.to_model(
            case_study,
            case_study_id=case_study.id,
            version=version,
        )
        db.add(db_case_study)
    db.flush()


def insert_relationships(
    db: Session, export: schemas.AtlasExport, version: str
) -> None:
    object_types = _object_types(export)
    for source, relationships_by_type in export.relationships.items():
        if source not in object_types:
            raise ValueError(
                f"Relationship source {source} does not exist in the export."
            )
        for relationship_type, entries in relationships_by_type.items():
            for index, entry in enumerate(entries, start=1):
                if (
                    entry.source != source
                    or entry.relationship_type != relationship_type
                ):
                    raise ValueError(
                        "Relationship fields must match their containing keys."
                    )
                if entry.target not in object_types:
                    raise ValueError(
                        f"Relationship target {entry.target} does not exist in the export."
                    )
                if source == entry.target:
                    raise ValueError("Relationship source and target must differ.")

                extra_fields = None
                if relationship_type == AtlasRelationshipType.SEQUENCES:
                    extra_fields = {"position": entry.position or index}
                elif relationship_type == AtlasRelationshipType.EMPLOYS:
                    extra_fields = {
                        "tactic": entry.tactic,
                        "step_id": entry.step_id,
                        "leads_to": entry.leads_to or [],
                    }
                elif entry.activity_purpose is not None:
                    extra_fields = {
                        "activity_purpose": entry.activity_purpose.value,
                    }

                validate_relationship_types(
                    object_types[source],
                    object_types[entry.target],
                    relationship_type,
                    extra_fields,
                )
                db.add(
                    models.Relationship(
                        source=source,
                        target=entry.target,
                        version=version,
                        relationship_type=relationship_type,
                        description=entry.description,
                        extra_fields=extra_fields,
                    )
                )
    db.flush()


def _object_types(export: schemas.AtlasExport) -> dict[str, AtlasObjectType]:
    object_types = {
        export.collection.id: AtlasObjectType.COLLECTION,
        export.matrix.id: AtlasObjectType.MATRIX,
    }
    mappings = (
        (export.tactics, AtlasObjectType.TACTIC),
        (export.techniques, AtlasObjectType.TECHNIQUE),
        (export.mitigations, AtlasObjectType.MITIGATION),
        (export.case_studies, AtlasObjectType.CASE_STUDY),
        (export.entities, AtlasObjectType.ENTITY),
        (export.software, AtlasObjectType.SOFTWARE),
    )
    for objects, object_type in mappings:
        object_types.update((obj.id, object_type) for obj in objects.values())
    return object_types


def insert_version_bundle(
    db: Session, export: schemas.AtlasExport, version: str
) -> None:
    insert_version_row(db, version)
    insert_collection(db, export, version)
    insert_matrix(db, export, version)
    insert_tactics(db, export, version)
    insert_techniques(db, export, version)
    insert_mitigations(db, export, version)
    insert_entities(db, export, version)
    insert_software(db, export, version)
    insert_case_studies(db, export, version)
    insert_relationships(db, export, version)


def print_summary(export: schemas.AtlasExport, version: str, mode: str) -> None:
    print("✅ Load complete!")
    print(f"  Mode: {mode}")
    print(f"  Version: {version}")
    print(f"  {len(export.tactics)} tactics")
    print(f"  {len(export.techniques)} techniques")
    print(f"  {len(export.mitigations)} mitigations")
    print(f"  {len(export.case_studies)} case studies")
    print(f"  {len(export.entities)} entities")
    print(f"  {len(export.software)} software")
    print(
        f"  {sum(len(e) for t in export.relationships.values() for e in t.values())} relationships"
    )


def populate_database(
    yaml_path: Path,
    *,
    force: bool = False,
    version_override: str | None = None,
) -> None:
    print("Upgrading database schema...")
    upgrade_database(engine)

    export = load_yaml_export(yaml_path)
    version = version_override or export.collection.version
    export.collection.version = version

    with SessionLocal() as db:
        ensure_format_version_set(db)
        assert_format_version_supported(db, export.format_version)

        existing = get_existing_version(db, version)
        if existing and not force:
            raise RuntimeError(
                f"Version {version} already exists. Re-run with --force to overwrite only this version."
            )

        mode = "create"
        if existing and force:
            print(f"Overwriting existing version {version} (--force)...")
            delete_version_data(db, version)
            db.flush()
            mode = "overwrite"

        insert_version_bundle(db, export, version)
        print("Committing...")
        db.commit()

    print_summary(export, version, mode)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", "-i", type=Path, default=Path("./dist/ATLAS-latest.yaml")
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Overwrite only matching version if it already exists",
    )
    parser.add_argument(
        "--version",
        "-v",
        type=str,
        default=None,
        help="Override version from YAML when loading",
    )
    args = parser.parse_args()

    populate_database(args.input, force=args.force, version_override=args.version)


if __name__ == "__main__":
    main()
