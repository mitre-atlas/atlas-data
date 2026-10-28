from typing import Annotated, Any

import yaml
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from atlas import mappers, schemas, services
from atlas.dependencies import get_db

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


# ---------------------------------------------------------------------------
# Health check (unversioned)
# ---------------------------------------------------------------------------


@router.get("/health")
def health_check():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------


@router.post("/versions", status_code=status.HTTP_201_CREATED)
def create_version(
    body: schemas.VersionCreateRequest,
    db: DbSession,
) -> schemas.VersionCreateResponse:
    return services.versions.create(db, body)


@router.get("/versions")
def get_versions(db: DbSession) -> list[schemas.Version]:
    return services.versions.get_all(db)


@router.patch("/versions/{version}")
def update_version(
    version: str,
    body: schemas.VersionUpdateRequest,
    db: DbSession,
) -> schemas.Version:
    return services.versions.update_metadata(db, version, body)


@router.delete("/versions/{version}")
def delete_version(version: str, db: DbSession) -> dict[str, str]:
    return services.versions.delete(db, version)


@router.get("/versions/{version}")
def get_version(version: str, db: DbSession) -> schemas.Version:
    version = services.versions.get_one(db, version)
    return mappers.versions.to_schema(version)


@router.get("/versions/{version}/data")
def export_collection(version: str, db: DbSession):
    export = services.export.build(db, version)
    data = export.model_dump(
        mode="json",
        exclude_none=True,
        by_alias=True,
    )
    yaml_str = yaml.dump(data, indent=2, sort_keys=False, allow_unicode=True)
    return Response(content=yaml_str, media_type="application/x-yaml")


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------


@router.get("/{version}/collection/")
def get_collection(
    version: str, db: DbSession
) -> schemas.CollectionResponse:
    collection = services.collections.get_one(db, version)
    return mappers.collections.to_schema(collection)


@router.put("/{version}/collection/")
def update_collection(
    version: str,
    body: schemas.CollectionInput,
    db: DbSession,
) -> schemas.CollectionResponse:
    collection = services.collections.update(db, version, body)
    return mappers.collections.to_schema(collection)


# ---------------------------------------------------------------------------
# Matrix
# ---------------------------------------------------------------------------


@router.get("/{version}/matrix/")
def get_matrix(version: str, db: DbSession):
    matrix = services.matrices.get_one(db, version)
    return mappers.matrices.to_schema(matrix)


@router.put("/{version}/matrix/")
def update_matrix(
    version: str,
    body: schemas.MatrixInput,
    db: DbSession,
) -> schemas.MatrixResponse:
    matrix = services.matrices.update(db, version, body)
    return mappers.matrices.to_schema(matrix)


# ---------------------------------------------------------------------------
# Tactics
# ---------------------------------------------------------------------------


@router.get("/{version}/tactics/")
def get_all_tactics(
    version: str, db: DbSession
) -> list[schemas.TacticResponse]:
    tactics = services.tactics.get_all(db, version)
    return [mappers.tactics.to_schema(t) for t in tactics]


@router.post("/{version}/tactics/", status_code=status.HTTP_201_CREATED)
def create_tactic(
    version: str,
    tactic: schemas.TacticInput,
    db: DbSession,
) -> schemas.TacticResponse:
    db_tactic = services.tactics.create(db, tactic, version)
    return mappers.tactics.to_schema(db_tactic)


@router.get("/{version}/tactics/{tactic_id}")
def get_tactic(
    version: str, tactic_id: str, db: DbSession
) -> schemas.TacticResponse:
    db_tactic = services.tactics.get_one(db, tactic_id, version)
    return mappers.tactics.to_schema(db_tactic)


@router.put("/{version}/tactics/{tactic_id}")
def update_tactic(
    version: str,
    tactic_id: str,
    tactic: schemas.TacticInput,
    db: DbSession,
) -> schemas.TacticResponse:
    db_tactic = services.tactics.update(db, tactic_id, version, tactic)
    return mappers.tactics.to_schema(db_tactic)


@router.delete("/{version}/tactics/{tactic_id}")
def delete_tactic(
    version: str, tactic_id: str, db: DbSession
) -> dict[str, Any]:
    return services.tactics.delete(db, tactic_id, version)


# ---------------------------------------------------------------------------
# Techniques
# ---------------------------------------------------------------------------


@router.get("/{version}/techniques/")
def get_all_techniques(
    version: str, db: DbSession
) -> list[schemas.TechniqueResponse]:
    db_techniques = services.techniques.get_all(db, version)
    return [mappers.techniques.to_schema(t) for t in db_techniques]


@router.post("/{version}/techniques/", status_code=status.HTTP_201_CREATED)
def create_technique(
    version: str,
    technique: schemas.TechniqueInput,
    db: DbSession,
) -> schemas.TechniqueResponse:
    db_technique = services.techniques.create(db, technique, version)
    return mappers.techniques.to_schema(db_technique)


@router.get("/{version}/techniques/{technique_id}")
def get_technique(
    version: str, technique_id: str, db: DbSession
) -> schemas.TechniqueResponse:
    db_technique = services.techniques.get_one(db, technique_id, version)
    return mappers.techniques.to_schema(db_technique)


@router.put("/{version}/techniques/{technique_id}")
def update_technique(
    version: str,
    technique_id: str,
    technique: schemas.TechniqueInput,
    db: DbSession,
) -> schemas.TechniqueResponse:
    db_technique = services.techniques.update(db, technique_id, version, technique)
    return mappers.techniques.to_schema(db_technique)


@router.delete("/{version}/techniques/{technique_id}")
def delete_technique(
    version: str, technique_id: str, db: DbSession
) -> dict[str, Any]:
    return services.techniques.delete(db, technique_id, version)


# ---------------------------------------------------------------------------
# Mitigations
# ---------------------------------------------------------------------------


@router.get("/{version}/mitigations/")
def get_all_mitigations(version: str, db: DbSession):
    mitigations = services.mitigations.get_all(db, version)
    return [mappers.mitigations.to_schema(db_m) for db_m in mitigations]


@router.post("/{version}/mitigations/", status_code=status.HTTP_201_CREATED)
def create_mitigation(
    version: str,
    mitigation: schemas.MitigationInput,
    db: DbSession,
) -> schemas.MitigationResponse:
    db_mitigation = services.mitigations.create(db, mitigation, version)
    return mappers.mitigations.to_schema(db_mitigation)


@router.get("/{version}/mitigations/{mitigation_id}")
def get_mitigation(
    version: str, mitigation_id: str, db: DbSession
) -> schemas.MitigationResponse:
    db_mitigation = services.mitigations.get_one(db, mitigation_id, version)
    return mappers.mitigations.to_schema(db_mitigation)


@router.put("/{version}/mitigations/{mitigation_id}")
def update_mitigation(
    version: str,
    mitigation_id: str,
    mitigation: schemas.MitigationInput,
    db: DbSession,
) -> schemas.MitigationResponse:
    db_mitigation = services.mitigations.update(db, mitigation_id, version, mitigation)
    return mappers.mitigations.to_schema(db_mitigation)


@router.delete("/{version}/mitigations/{mitigation_id}")
def delete_mitigation(
    version: str, mitigation_id: str, db: DbSession
) -> dict[str, Any]:
    return services.mitigations.delete(db, mitigation_id, version)


# ---------------------------------------------------------------------------
# Entities
# ---------------------------------------------------------------------------


@router.get("/{version}/entities/")
def get_all_entities(
    version: str, db: DbSession
) -> list[schemas.EntityResponse]:
    entities = services.entities.get_all(db, version)
    return [mappers.entities.to_schema(entity) for entity in entities]


@router.post("/{version}/entities/", status_code=status.HTTP_201_CREATED)
def create_entity(
    version: str,
    entity: schemas.EntityInput,
    db: DbSession,
) -> schemas.EntityResponse:
    db_entity = services.entities.create(db, entity, version)
    return mappers.entities.to_schema(db_entity)


@router.get("/{version}/entities/{entity_id}")
def get_entity(
    version: str, entity_id: str, db: DbSession
) -> schemas.EntityResponse:
    db_entity = services.entities.get_one(db, entity_id, version)
    return mappers.entities.to_schema(db_entity)


@router.put("/{version}/entities/{entity_id}")
def update_entity(
    version: str,
    entity_id: str,
    entity: schemas.EntityInput,
    db: DbSession,
) -> schemas.EntityResponse:
    db_entity = services.entities.update(db, entity_id, version, entity)
    return mappers.entities.to_schema(db_entity)


@router.delete("/{version}/entities/{entity_id}")
def delete_entity(
    version: str, entity_id: str, db: DbSession
) -> dict[str, Any]:
    return services.entities.delete(db, entity_id, version)


# ---------------------------------------------------------------------------
# Software
# ---------------------------------------------------------------------------


@router.get("/{version}/software/")
def get_all_software(
    version: str, db: DbSession
) -> list[schemas.SoftwareResponse]:
    software = services.software.get_all(db, version)
    return [mappers.software.to_schema(db_software) for db_software in software]


@router.post("/{version}/software/", status_code=status.HTTP_201_CREATED)
def create_software(
    version: str,
    software: schemas.SoftwareInput,
    db: DbSession,
) -> schemas.SoftwareResponse:
    db_software = services.software.create(db, software, version)
    return mappers.software.to_schema(db_software)


@router.get("/{version}/software/{software_id}")
def get_software(
    version: str, software_id: str, db: DbSession
) -> schemas.SoftwareResponse:
    db_software = services.software.get_one(db, software_id, version)
    return mappers.software.to_schema(db_software)


@router.put("/{version}/software/{software_id}")
def update_software(
    version: str,
    software_id: str,
    software: schemas.SoftwareInput,
    db: DbSession,
) -> schemas.SoftwareResponse:
    db_software = services.software.update(db, software_id, version, software)
    return mappers.software.to_schema(db_software)


@router.delete("/{version}/software/{software_id}")
def delete_software(
    version: str, software_id: str, db: DbSession
) -> dict[str, Any]:
    return services.software.delete(db, software_id, version)


# ---------------------------------------------------------------------------
# Case Studies
# ---------------------------------------------------------------------------


@router.post("/{version}/case-studies/", status_code=status.HTTP_201_CREATED)
def create_case_study(
    version: str,
    case_study: schemas.CaseStudyInput,
    db: DbSession,
) -> schemas.CaseStudyResponse:
    db_case_study = services.case_studies.create(db, case_study, version)
    return mappers.case_studies.to_schema(db_case_study)


@router.get("/{version}/case-studies/{case_study_id}")
def get_case_study(
    version: str, case_study_id: str, db: DbSession
) -> schemas.CaseStudyResponse:
    db_case_study = services.case_studies.get_one(db, case_study_id, version)
    return mappers.case_studies.to_schema(db_case_study)


@router.get("/{version}/case-studies/")
def get_all_case_studies(
    version: str, db: DbSession
) -> list[schemas.CaseStudyResponse]:
    case_studies = services.case_studies.get_all(db, version)
    return [mappers.case_studies.to_schema(db_cs) for db_cs in case_studies]


@router.put("/{version}/case-studies/{case_study_id}")
def update_case_study(
    version: str,
    case_study_id: str,
    case_study: schemas.CaseStudyInput,
    db: DbSession,
) -> schemas.CaseStudyResponse:
    db_case_study = services.case_studies.update(db, case_study_id, version, case_study)
    return mappers.case_studies.to_schema(db_case_study)


@router.delete("/{version}/case-studies/{case_study_id}")
def delete_case_study(
    version: str, case_study_id: str, db: DbSession
) -> dict[str, Any]:
    return services.case_studies.delete(db, case_study_id, version)
