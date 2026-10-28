from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator

import pytest
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

import atlas.services.versions as versions_service
import atlas.api as api_module
from atlas import models, schemas, services
from atlas.api import app
from atlas.constants import (
    ATLAS_COLLECTION_ID,
    ATLAS_FORMAT_VERSION,
    ATLAS_MATRIX_ID,
)
from atlas.db import Base
from atlas.dependencies import get_db
from atlas.enums import (
    AtlasRelationshipType,
    MitigationCategoryType,
    MitigationLifecyclePhasesType,
    TechniquePlatformType,
)
from atlas.services.format_versions import ATLAS_FORMAT_VERSION_ROW_ID

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

ATLAS_DATA_VERSION = "2026.05"


@pytest.fixture(scope="session")
def test_engine() -> Engine:
    engine = create_engine(
        "sqlite:///:memory:", echo=False, connect_args={"check_same_thread": False}
    )

    @event.listens_for(engine, "connect")
    def set_pragma(dbapi_connection: Any, connection_record: Any) -> None:
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture()
def test_session(test_engine: Engine) -> Iterator[Session]:
    conn = test_engine.connect()
    trans = conn.begin()
    TestSession = sessionmaker(bind=conn)
    session = TestSession()
    yield session
    session.close()
    if trans.is_active:
        trans.rollback()
    conn.close()


@pytest.fixture()
def client(
    test_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    registered_versions: tuple[str, ...],
) -> Iterator[TestClient]:
    # CRUD fixtures need registered versions; version-management tests start empty.
    test_session.add_all(models.Version(version=v) for v in registered_versions)
    test_session.commit()
    if test_session.get(models.FormatVersion, ATLAS_FORMAT_VERSION_ROW_ID) is None:
        test_session.add(
            models.FormatVersion(
                id=ATLAS_FORMAT_VERSION_ROW_ID,
                version=ATLAS_FORMAT_VERSION,
            )
        )
        test_session.commit()
    test_session_factory = sessionmaker(bind=test_session.get_bind())
    app.dependency_overrides[get_db] = lambda: test_session
    monkeypatch.setattr(api_module, "SessionLocal", test_session_factory)
    monkeypatch.setattr(api_module, "ensure_database_current", lambda engine: None)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def db(client: TestClient) -> Session:
    fastapi_app = client.app
    assert isinstance(fastapi_app, FastAPI)
    return fastapi_app.dependency_overrides[get_db]()


@pytest.fixture()
def registered_versions() -> tuple[str, ...]:
    return (ATLAS_DATA_VERSION,)


@pytest.fixture()
def seed_collection(db: Session) -> str:
    db.add(
        models.Collection(
            id="ATLAS-collection",
            version=ATLAS_DATA_VERSION,
            name="Test Collection",
            description="Test",
        )
    )
    db.commit()
    return "ATLAS-collection"


@pytest.fixture()
def seed_matrix(db: Session) -> str:
    db.add(
        models.Matrix(
            id="ATLAS-matrix",
            version=ATLAS_DATA_VERSION,
            name="Test Matrix",
            description="Test",
        )
    )
    db.commit()
    return "ATLAS-matrix"


@pytest.fixture()
def seed_collection_and_matrix(
    seed_collection: str, seed_matrix: str
) -> tuple[str, str]:
    return seed_collection, seed_matrix


@pytest.fixture(scope="session")
def atlas_latest_export() -> schemas.AtlasExport:
    atlas_path = Path(__file__).resolve().parent.parent / "dist" / "ATLAS-latest.yaml"
    data = yaml.safe_load(atlas_path.read_text(encoding="utf-8"))
    return schemas.AtlasExport(**data)


@pytest.fixture()
def loaded_real_dataset(
    db: Session, atlas_latest_export: schemas.AtlasExport
) -> tuple[str, schemas.AtlasExport]:
    version = "99.99.99-roundtrip"
    export = atlas_latest_export

    db.add(
        models.Version(
            version=version,
            base_version=None,
            created_date=export.collection.created_date,
            modified_date=export.collection.modified_date,
            publish_date=None,
        )
    )
    db.flush()

    db.add(
        models.Collection(
            id=ATLAS_COLLECTION_ID,
            version=version,
            name=export.collection.name,
            description=export.collection.description,
            references=[
                ref.model_dump(mode="json") for ref in export.collection.references
            ],
            created_date=export.collection.created_date,
            modified_date=export.collection.modified_date,
        )
    )
    db.add(
        models.Matrix(
            id=ATLAS_MATRIX_ID,
            version=version,
            name=export.matrix.name,
            description=export.matrix.description,
            references=[
                ref.model_dump(mode="json") for ref in export.matrix.references
            ],
            created_date=export.matrix.created_date,
            modified_date=export.matrix.modified_date,
        )
    )

    for tactic in export.tactics.values():
        db.add(
            models.Tactic(
                id=tactic.id,
                version=version,
                name=tactic.name,
                description=tactic.description,
                references=[ref.model_dump(mode="json") for ref in tactic.references],
                created_date=tactic.created_date,
                modified_date=tactic.modified_date,
                attack_reference=(
                    tactic.attack_reference.model_dump(mode="json")
                    if tactic.attack_reference
                    else None
                ),
            )
        )

    for technique in export.techniques.values():
        db.add(
            models.Technique(
                id=technique.id,
                version=version,
                name=technique.name,
                description=technique.description,
                references=[
                    ref.model_dump(mode="json") for ref in technique.references
                ],
                created_date=technique.created_date,
                modified_date=technique.modified_date,
                maturity=technique.maturity,
                platforms=[platform.value for platform in technique.platforms],
                attack_reference=(
                    technique.attack_reference.model_dump(mode="json")
                    if technique.attack_reference
                    else None
                ),
            )
        )

    for mitigation in export.mitigations.values():
        db.add(
            models.Mitigation(
                id=mitigation.id,
                version=version,
                name=mitigation.name,
                description=mitigation.description,
                references=[
                    ref.model_dump(mode="json") for ref in mitigation.references
                ],
                created_date=mitigation.created_date,
                modified_date=mitigation.modified_date,
                lifecycle_phases=[phase.value for phase in mitigation.lifecycle_phases],
                categories=[category.value for category in mitigation.categories],
                attack_reference=(
                    mitigation.attack_reference.model_dump(mode="json")
                    if mitigation.attack_reference
                    else None
                ),
            )
        )

    for case_study in export.case_studies.values():
        db.add(
            models.CaseStudy(
                id=case_study.id,
                version=version,
                name=case_study.name,
                description=case_study.description,
                references=[
                    ref.model_dump(mode="json") for ref in case_study.references
                ],
                created_date=case_study.created_date,
                modified_date=case_study.modified_date,
                type=case_study.type,
                actor=case_study.actor,
                target=case_study.target,
                reporter=case_study.reporter,
                start_date=case_study.start_date,
                start_date_granularity=case_study.start_date_granularity,
                end_date=case_study.end_date,
                end_date_granularity=case_study.end_date_granularity,
            )
        )

    from tools.populate_atlas_db import insert_entities, insert_software

    insert_entities(db, export, version)
    insert_software(db, export, version)

    for source, rels_by_type in export.relationships.items():
        for rel_type, entries in rels_by_type.items():
            for entry in entries:
                extra_fields = None
                if rel_type == models.AtlasRelationshipType.EMPLOYS:
                    extra_fields = {
                        "tactic": entry.tactic,
                        "step_id": entry.step_id,
                        "leads_to": entry.leads_to or [],
                    }
                elif rel_type == models.AtlasRelationshipType.SEQUENCES:
                    extra_fields = {"position": entry.position}
                elif entry.activity_purpose is not None:
                    extra_fields = {"activity_purpose": entry.activity_purpose.value}

                db.add(
                    models.Relationship(
                        source=source,
                        target=entry.target,
                        version=version,
                        relationship_type=rel_type,
                        description=entry.description,
                        extra_fields=extra_fields,
                    )
                )

    db.commit()
    return version, export


# ---------------------------------------------------------------------------
# Payload factories (no id — server generates)
# ---------------------------------------------------------------------------


def tactic_payload(**overrides: Any) -> dict[str, Any]:
    data = dict(
        name="Test Tactic",
        description="A test tactic",
    )
    data.update(overrides)
    return data


def technique_payload(**overrides: Any) -> dict[str, Any]:
    data = dict(
        name="Test Technique",
        description="A test technique",
        tactics=[{"tactic": "AML.TA0001"}],
        platforms=["Agentic AI"],
    )
    data.update(overrides)
    return data


def mitigation_payload(**overrides: Any) -> dict[str, Any]:
    data = dict(
        name="Test Mitigation",
        description="A test mitigation",
        mitigates=[{"technique": "AML.T0001"}],
        lifecycle_phases=["Deployment"],
        categories=["Policy"],
    )
    data.update(overrides)
    return data


def case_study_payload(**overrides: Any) -> dict[str, Any]:
    data = dict(
        name="Test Case Study",
        description="A test case study",
        type="Incident",
        actor="Test Actor",
        target="Test Target",
        reporter="Test Reporter",
        date="2024-01-15",
        date_granularity="Day",
        attack_chain=[
            dict(
                technique="AML.T0001",
                tactic="AML.TA0001",
                step_id="S01",
                leads_to=["S02"],
            ),
        ],
    )
    data.update(overrides)
    data["attributed_to"] = [
        {
            **attribution,
            "activity_purpose": attribution.get(
                "activity_purpose", "Adversarial Operation"
            ),
        }
        for attribution in data.get("attributed_to", [])
    ]
    return data


def entity_payload(**overrides: Any) -> dict[str, Any]:
    data = dict(
        name="Test Entity",
        description="A test entity",
        entity_type="Activity Cluster",
        associated_entities=[],
        uses=[],
    )
    data.update(overrides)
    data["uses"] = [
        {
            **use,
            **(
                {
                    "activity_purpose": use.get(
                        "activity_purpose", "Adversarial Operation"
                    )
                }
                if "technique" in use
                else {}
            ),
        }
        for use in data["uses"]
    ]
    return data


def software_payload(**overrides: Any) -> dict[str, Any]:
    data = dict(
        name="Test Software",
        description="Test software",
        software_type="Malware",
        implements=[],
    )
    data.update(overrides)
    return data


def create_tactic(client: TestClient, **overrides: Any) -> str:
    resp = client.post(
        f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload(**overrides)
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def create_technique(client: TestClient, tactic_id: str, **overrides: Any) -> str:
    default_tactics = [{"tactic": tactic_id}]
    if "tactics" in overrides:
        default_tactics = overrides.pop("tactics")
    payload = technique_payload(tactics=default_tactics, **overrides)
    resp = client.post(f"/{ATLAS_DATA_VERSION}/techniques/", json=payload)
    assert resp.status_code == 201
    return resp.json()["id"]


def create_mitigation(client: TestClient, technique_id: str, **overrides: Any) -> str:
    payload = mitigation_payload(mitigates=[{"technique": technique_id}], **overrides)
    resp = client.post(f"/{ATLAS_DATA_VERSION}/mitigations/", json=payload)
    assert resp.status_code == 201
    return resp.json()["id"]


def create_case_study(
    client: TestClient,
    tactic_id: str,
    technique_id: str,
    **overrides: Any,
) -> str:
    default_chain = [
        dict(technique=technique_id, tactic=tactic_id, step_id="S01", leads_to=["S02"])
    ]
    if "attack_chain" in overrides:
        default_chain = overrides.pop("attack_chain")
    payload = case_study_payload(attack_chain=default_chain, **overrides)
    resp = client.post(f"/{ATLAS_DATA_VERSION}/case-studies/", json=payload)
    assert resp.status_code == 201
    return resp.json()["id"]


def create_entity(
    client: TestClient,
    *,
    version: str = ATLAS_DATA_VERSION,
    **overrides: Any,
) -> str:
    resp = client.post(f"/{version}/entities/", json=entity_payload(**overrides))
    assert resp.status_code == 201
    return resp.json()["id"]


def create_software(
    client: TestClient,
    *,
    version: str = ATLAS_DATA_VERSION,
    **overrides: Any,
) -> str:
    resp = client.post(f"/{version}/software/", json=software_payload(**overrides))
    assert resp.status_code == 201
    return resp.json()["id"]


def add_matrix_sequence(
    db: Session,
    tactic_id: str,
    position: int | None = None,
    description: str | None = None,
) -> None:
    extra_fields = None
    if position is not None:
        extra_fields = {"position": position}
    db.add(
        models.Relationship(
            source="ATLAS-matrix",
            target=tactic_id,
            version=ATLAS_DATA_VERSION,
            relationship_type=models.AtlasRelationshipType.SEQUENCES,
            description=description,
            extra_fields=extra_fields,
        )
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class TestHealth:
    def test_health(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Tactics
# ---------------------------------------------------------------------------


class TestTactics:
    def test_create_tactic(self, client: TestClient) -> None:
        resp = client.post(f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload())
        assert resp.status_code == 201
        body = resp.json()
        assert body["id"] == "AML.TA0001"
        assert body["name"] == "Test Tactic"
        assert body["object-type"] == "tactic"
        assert "uuid" in body

    def test_get_all_tactics_empty(self, client: TestClient) -> None:
        resp = client.get(f"/{ATLAS_DATA_VERSION}/tactics/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_all_tactics(self, client: TestClient) -> None:
        create_tactic(client)
        create_tactic(client, name="Tactic 2")
        resp = client.get(f"/{ATLAS_DATA_VERSION}/tactics/")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2
        ids = {t["id"] for t in body}
        assert ids == {"AML.TA0001", "AML.TA0002"}

    def test_get_tactic_by_id(self, client: TestClient) -> None:
        tactic_id = create_tactic(client)
        resp = client.get(f"/{ATLAS_DATA_VERSION}/tactics/{tactic_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == tactic_id

    def test_update_tactic(self, client: TestClient) -> None:
        tactic_id = create_tactic(client)
        update = tactic_payload(name="Updated Tactic")
        resp = client.put(f"/{ATLAS_DATA_VERSION}/tactics/{tactic_id}", json=update)
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Tactic"

    def test_delete_tactic(self, client: TestClient) -> None:
        tactic_id = create_tactic(client)
        resp = client.delete(f"/{ATLAS_DATA_VERSION}/tactics/{tactic_id}")
        assert resp.status_code == 200
        get_resp = client.get(f"/{ATLAS_DATA_VERSION}/tactics/{tactic_id}")
        assert get_resp.status_code == 404

    def test_create_tactic_with_references(self, client: TestClient) -> None:
        payload = tactic_payload(
            references=[
                {"id": "ref-1", "title": "Ref 1", "url": "https://example.com"}
            ],
        )
        resp = client.post(f"/{ATLAS_DATA_VERSION}/tactics/", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert len(body["references"]) == 1
        assert body["references"][0]["title"] == "Ref 1"

    def test_create_tactic_with_attack_reference(self, client: TestClient) -> None:
        payload = tactic_payload(
            attack_reference={
                "id": "TA0001",
                "url": "https://attack.mitre.org/techniques/TA0001",
            },
        )
        resp = client.post(f"/{ATLAS_DATA_VERSION}/tactics/", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert body["attack-reference"]["id"] == "TA0001"

    def test_create_tactic_invalid_body(self, client: TestClient) -> None:
        resp = client.post(
            f"/{ATLAS_DATA_VERSION}/tactics/", json={"name": "No description"}
        )
        assert resp.status_code == 422

    def test_create_tactic_id_forbidden(self, client: TestClient) -> None:
        """id field should be rejected on create."""
        payload = tactic_payload(id="AML.TA9999")
        resp = client.post(f"/{ATLAS_DATA_VERSION}/tactics/", json=payload)
        assert resp.status_code == 422

    def test_create_tactic_extra_field_forbidden(self, client: TestClient) -> None:
        payload = tactic_payload(unknown_field="should not be allowed")
        resp = client.post(f"/{ATLAS_DATA_VERSION}/tactics/", json=payload)
        assert resp.status_code == 422


@pytest.mark.parametrize(
    ("label", "create_path", "seed"),
    [
        (
            "tactic",
            f"/{ATLAS_DATA_VERSION}/tactics/",
            lambda client: None,
        ),
        (
            "technique",
            f"/{ATLAS_DATA_VERSION}/techniques/",
            lambda client: create_tactic(client),
        ),
        (
            "mitigation",
            f"/{ATLAS_DATA_VERSION}/mitigations/",
            lambda client: create_technique(client, create_tactic(client)),
        ),
        (
            "case-study",
            f"/{ATLAS_DATA_VERSION}/case-studies/",
            lambda client: create_technique(client, create_tactic(client)),
        ),
    ],
)
def test_duplicate_create_generates_new_id(
    client: TestClient,
    label: str,
    create_path: str,
    seed: Callable[[TestClient], None],
) -> None:
    seed(client)
    if label == "tactic":
        payload = tactic_payload()
    elif label == "technique":
        payload = technique_payload(tactics=[{"tactic": "AML.TA0001"}])
    elif label == "mitigation":
        payload = mitigation_payload(mitigates=[{"technique": "AML.T0001"}])
    else:
        payload = case_study_payload(
            attack_chain=[
                dict(
                    technique="AML.T0001",
                    tactic="AML.TA0001",
                    step_id="S01",
                    leads_to=["S02"],
                )
            ]
        )

    resp1 = client.post(create_path, json=payload)
    assert resp1.status_code == 201
    resp2 = client.post(create_path, json=payload)
    assert resp2.status_code == 201
    assert resp2.json()["id"] != resp1.json()["id"]


@pytest.mark.parametrize(
    ("path", "missing_id"),
    [
        (f"/{ATLAS_DATA_VERSION}/tactics/{{id}}", "AML.TA9999"),
        (f"/{ATLAS_DATA_VERSION}/techniques/{{id}}", "AML.T9999"),
        (f"/{ATLAS_DATA_VERSION}/mitigations/{{id}}", "AML.M9999"),
        (f"/{ATLAS_DATA_VERSION}/case-studies/{{id}}", "AML.CS9999"),
    ],
)
def test_get_by_id_not_found(client: TestClient, path: str, missing_id: str) -> None:
    assert client.get(path.format(id=missing_id)).status_code == 404


@pytest.mark.parametrize(
    ("path", "missing_id"),
    [
        (f"/{ATLAS_DATA_VERSION}/tactics/{{id}}", "AML.TA9999"),
        (f"/{ATLAS_DATA_VERSION}/techniques/{{id}}", "AML.T9999"),
        (f"/{ATLAS_DATA_VERSION}/mitigations/{{id}}", "AML.M9999"),
        (f"/{ATLAS_DATA_VERSION}/case-studies/{{id}}", "AML.CS9999"),
    ],
)
def test_delete_by_id_not_found(client: TestClient, path: str, missing_id: str) -> None:
    assert client.delete(path.format(id=missing_id)).status_code == 404


# ---------------------------------------------------------------------------
# Techniques
# ---------------------------------------------------------------------------


class TestTechniques:
    @pytest.mark.parametrize("maturity", [None, "Demonstrated", "Realized"])
    def test_create_technique(self, client: TestClient, maturity) -> None:
        tactic_id = create_tactic(client)
        payload = technique_payload(tactics=[{"tactic": tactic_id}])
        if maturity is not None:
            payload["maturity"] = maturity
        resp = client.post(f"/{ATLAS_DATA_VERSION}/techniques/", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert body["id"] == "AML.T0001"
        assert body["maturity"] == (maturity or "Feasible")
        assert body["object-type"] == "technique"

    def test_get_all_techniques(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        create_technique(client, t1_id)
        create_technique(client, t1_id, name="Technique 2")
        resp = client.get(f"/{ATLAS_DATA_VERSION}/techniques/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_technique_by_id(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_id = create_technique(client, t1_id)
        resp = client.get(f"/{ATLAS_DATA_VERSION}/techniques/{tech_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == tech_id

    def test_update_technique(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_id = create_technique(client, t1_id)
        resp = client.put(
            f"/{ATLAS_DATA_VERSION}/techniques/{tech_id}",
            json=technique_payload(name="Updated Technique", maturity="Realized"),
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Technique"
        assert resp.json()["maturity"] == "Realized"
        for maturity in (None, "Demonstrated", "Feasible"):
            payload = technique_payload(name="Updated Technique")
            if maturity is not None:
                payload["maturity"] = maturity
            resp = client.put(
                f"/{ATLAS_DATA_VERSION}/techniques/{tech_id}", json=payload
            )
            assert resp.status_code == 200
            assert resp.json()["maturity"] == (maturity or "Realized")
        invalid = client.put(
            f"/{ATLAS_DATA_VERSION}/techniques/{tech_id}",
            json=technique_payload(maturity="Unknown"),
        )
        assert invalid.status_code == 422

    def test_delete_technique(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_id = create_technique(client, t1_id)
        resp = client.delete(f"/{ATLAS_DATA_VERSION}/techniques/{tech_id}")
        assert resp.status_code == 200
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{tech_id}").status_code == 404
        )

    def test_create_technique_with_platforms(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        payload = technique_payload(
            tactics=[{"tactic": t1_id}],
            platforms=["Agentic AI", "Predictive AI", "Generative AI"],
            references=[
                {
                    "id": "tech-ref",
                    "title": "Tech Ref",
                    "url": "https://example.com/tech",
                }
            ],
        )
        resp = client.post(f"/{ATLAS_DATA_VERSION}/techniques/", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert (
            body["platforms"]
            == [platform.value for platform in TechniquePlatformType][:3]
        )
        assert len(body["references"]) == 1

    def test_create_technique_empty_platforms_rejected(
        self, client: TestClient
    ) -> None:
        tactic_id = create_tactic(client)
        payload = technique_payload(tactics=[{"tactic": tactic_id}], platforms=[])
        resp = client.post(f"/{ATLAS_DATA_VERSION}/techniques/", json=payload)
        assert resp.status_code == 422

    def test_create_subtechnique(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        parent_id = create_technique(client, t1_id)
        payload = technique_payload(
            tactics=[{"tactic": t1_id}],
            name="Test Subtechnique",
            specializes={"technique": parent_id},
        )
        resp = client.post(f"/{ATLAS_DATA_VERSION}/techniques/", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert body["id"] == f"{parent_id}.000"
        assert body["specializes"] is not None
        assert body["specializes"]["technique"] == parent_id

        second_resp = client.post(f"/{ATLAS_DATA_VERSION}/techniques/", json=payload)
        assert second_resp.status_code == 201
        assert second_resp.json()["id"] == f"{parent_id}.001"

    def test_create_subtechnique_rejects_tactic_mismatch(
        self, client: TestClient
    ) -> None:
        t1_id = create_tactic(client)
        t2_id = create_tactic(client, name="Tactic 2")
        parent_id = create_technique(client, t1_id)
        payload = technique_payload(
            tactics=[{"tactic": t2_id}],
            name="Mismatched Subtechnique",
            specializes={"technique": parent_id},
        )
        resp = client.post(f"/{ATLAS_DATA_VERSION}/techniques/", json=payload)
        assert resp.status_code == 409

    def test_update_subtechnique_rejects_tactic_mismatch(
        self, client: TestClient
    ) -> None:
        t1_id = create_tactic(client)
        t2_id = create_tactic(client, name="Tactic 2")
        parent_id = create_technique(client, t1_id)
        child_id = client.post(
            f"/{ATLAS_DATA_VERSION}/techniques/",
            json=technique_payload(
                tactics=[{"tactic": t1_id}],
                name="Child",
                specializes={"technique": parent_id},
            ),
        ).json()["id"]

        resp = client.put(
            f"/{ATLAS_DATA_VERSION}/techniques/{child_id}",
            json=technique_payload(
                name="Child Updated",
                tactics=[{"tactic": t2_id}],
                specializes={"technique": parent_id},
            ),
        )
        assert resp.status_code == 409

    def test_update_subtechnique_with_matching_tactics_succeeds(
        self, client: TestClient
    ) -> None:
        t1_id = create_tactic(client)
        parent_id = create_technique(client, t1_id)
        child_id = client.post(
            f"/{ATLAS_DATA_VERSION}/techniques/",
            json=technique_payload(
                tactics=[{"tactic": t1_id}],
                name="Child",
                specializes={"technique": parent_id},
            ),
        ).json()["id"]

        resp = client.put(
            f"/{ATLAS_DATA_VERSION}/techniques/{child_id}",
            json=technique_payload(
                name="Child Updated",
                tactics=[{"tactic": t1_id}],
                specializes={"technique": parent_id},
            ),
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Child Updated"
        assert [item["tactic"] for item in resp.json()["tactics"]] == [t1_id]

    def test_update_subtechnique_preserves_submitted_tactic_description(
        self, client: TestClient
    ) -> None:
        t1_id = create_tactic(client)
        parent_id = create_technique(client, t1_id)
        child_id = client.post(
            f"/{ATLAS_DATA_VERSION}/techniques/",
            json=technique_payload(
                tactics=[{"tactic": t1_id, "description": "Initial rationale"}],
                name="Child",
                specializes={"technique": parent_id},
            ),
        ).json()["id"]

        response = client.put(
            f"/{ATLAS_DATA_VERSION}/techniques/{child_id}",
            json=technique_payload(
                tactics=[{"tactic": t1_id, "description": "Updated rationale"}],
                name="Child Updated",
                specializes={"technique": parent_id},
            ),
        )

        assert response.status_code == 200
        assert response.json()["tactics"][0]["description"] == "Updated rationale"

    def test_update_parent_technique_propagates_tactics_to_subtechniques(
        self, client: TestClient
    ) -> None:
        t1_id = create_tactic(client)
        t2_id = create_tactic(client, name="Tactic 2")
        parent_id = create_technique(client, t1_id)
        child_id = client.post(
            f"/{ATLAS_DATA_VERSION}/techniques/",
            json=technique_payload(
                tactics=[{"tactic": t1_id}],
                name="Child",
                specializes={"technique": parent_id},
            ),
        ).json()["id"]

        update_resp = client.put(
            f"/{ATLAS_DATA_VERSION}/techniques/{parent_id}",
            json=technique_payload(name="Parent Updated", tactics=[{"tactic": t2_id}]),
        )
        assert update_resp.status_code == 200
        assert [item["tactic"] for item in update_resp.json()["tactics"]] == [t2_id]

        child_resp = client.get(f"/{ATLAS_DATA_VERSION}/techniques/{child_id}")
        assert child_resp.status_code == 200
        assert [item["tactic"] for item in child_resp.json()["tactics"]] == [t2_id]

    def test_update_parent_preserves_child_tactic_description(
        self, client: TestClient
    ) -> None:
        t1_id = create_tactic(client)
        parent_id = create_technique(client, t1_id)
        child_id = client.post(
            f"/{ATLAS_DATA_VERSION}/techniques/",
            json=technique_payload(
                tactics=[{"tactic": t1_id, "description": "Child rationale"}],
                name="Child",
                specializes={"technique": parent_id},
            ),
        ).json()["id"]

        response = client.put(
            f"/{ATLAS_DATA_VERSION}/techniques/{parent_id}",
            json=technique_payload(name="Parent Renamed", tactics=[{"tactic": t1_id}]),
        )

        assert response.status_code == 200
        child = client.get(f"/{ATLAS_DATA_VERSION}/techniques/{child_id}")
        assert child.json()["tactics"][0]["description"] == "Child rationale"

    def test_delete_parent_technique_cascades_to_subtechniques(
        self, client: TestClient
    ) -> None:
        t1_id = create_tactic(client)
        parent_id = create_technique(client, t1_id)
        child_id = client.post(
            f"/{ATLAS_DATA_VERSION}/techniques/",
            json=technique_payload(
                tactics=[{"tactic": t1_id}],
                name="Child",
                specializes={"technique": parent_id},
            ),
        ).json()["id"]

        delete_resp = client.delete(f"/{ATLAS_DATA_VERSION}/techniques/{parent_id}")
        assert delete_resp.status_code == 200
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{parent_id}").status_code
            == 404
        )
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{child_id}").status_code
            == 404
        )

    def test_create_subtechnique_rejects_subtechnique_parent_id(
        self, client: TestClient
    ) -> None:
        t1_id = create_tactic(client)
        root_id = create_technique(client, t1_id)
        intermediate_id = client.post(
            f"/{ATLAS_DATA_VERSION}/techniques/",
            json=technique_payload(
                tactics=[{"tactic": t1_id}],
                name="Intermediate",
                specializes={"technique": root_id},
            ),
        ).json()["id"]

        resp = client.post(
            f"/{ATLAS_DATA_VERSION}/techniques/",
            json=technique_payload(
                tactics=[{"tactic": t1_id}],
                name="Leaf",
                specializes={"technique": intermediate_id},
            ),
        )
        assert resp.status_code == 422

    def test_update_subtechnique_rejects_subtechnique_parent_id(
        self, client: TestClient
    ) -> None:
        t1_id = create_tactic(client)
        root_id = create_technique(client, t1_id)
        intermediate_id = client.post(
            f"/{ATLAS_DATA_VERSION}/techniques/",
            json=technique_payload(
                tactics=[{"tactic": t1_id}],
                name="Intermediate",
                specializes={"technique": root_id},
            ),
        ).json()["id"]
        leaf_id = create_technique(client, t1_id, name="Leaf")

        resp = client.put(
            f"/{ATLAS_DATA_VERSION}/techniques/{leaf_id}",
            json=technique_payload(
                name="Leaf Updated",
                tactics=[{"tactic": t1_id}],
                specializes={"technique": intermediate_id},
            ),
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Mitigations
# ---------------------------------------------------------------------------


class TestMitigations:
    def test_create_mitigation(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_id = create_technique(client, t1_id)
        payload = mitigation_payload(mitigates=[{"technique": tech_id}])
        resp = client.post(f"/{ATLAS_DATA_VERSION}/mitigations/", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert body["id"] == "AML.M0001"
        assert body["object-type"] == "mitigation"

    def test_get_all_mitigations(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_id = create_technique(client, t1_id)
        payload = mitigation_payload(mitigates=[{"technique": tech_id}])
        client.post(f"/{ATLAS_DATA_VERSION}/mitigations/", json=payload)
        client.post(
            f"/{ATLAS_DATA_VERSION}/mitigations/",
            json={**payload, "name": "Mitigation 2"},
        )
        resp = client.get(f"/{ATLAS_DATA_VERSION}/mitigations/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_mitigation_by_id(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_id = create_technique(client, t1_id)
        payload = mitigation_payload(mitigates=[{"technique": tech_id}])
        resp = client.post(f"/{ATLAS_DATA_VERSION}/mitigations/", json=payload)
        mid = resp.json()["id"]
        resp = client.get(f"/{ATLAS_DATA_VERSION}/mitigations/{mid}")
        assert resp.status_code == 200

    def test_update_mitigation(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_id = create_technique(client, t1_id)
        payload = mitigation_payload(mitigates=[{"technique": tech_id}])
        resp = client.post(f"/{ATLAS_DATA_VERSION}/mitigations/", json=payload)
        mid = resp.json()["id"]
        resp = client.put(
            f"/{ATLAS_DATA_VERSION}/mitigations/{mid}",
            json=mitigation_payload(name="Updated Mitigation"),
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Mitigation"

    def test_delete_mitigation(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_id = create_technique(client, t1_id)
        payload = mitigation_payload(mitigates=[{"technique": tech_id}])
        resp = client.post(f"/{ATLAS_DATA_VERSION}/mitigations/", json=payload)
        mid = resp.json()["id"]
        resp = client.delete(f"/{ATLAS_DATA_VERSION}/mitigations/{mid}")
        assert resp.status_code == 200
        assert client.get(f"/{ATLAS_DATA_VERSION}/mitigations/{mid}").status_code == 404

    def test_create_mitigation_with_lifecycle(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_id = create_technique(client, t1_id)
        payload = mitigation_payload(
            mitigates=[{"technique": tech_id}],
            lifecycle_phases=["Deployment", "AI Model Evaluation"],
            categories=["Technical - Cyber", "Policy", "Technical - AI"],
        )
        resp = client.post(f"/{ATLAS_DATA_VERSION}/mitigations/", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert body["lifecycle-phases"] == [
            MitigationLifecyclePhasesType.MODEL_EVALUATION.value,
            MitigationLifecyclePhasesType.DEPLOYMENT.value,
        ]
        assert body["categories"] == [
            category.value for category in MitigationCategoryType
        ]

    def test_create_mitigation_empty_lists_rejected(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_id = create_technique(client, t1_id)
        payload = mitigation_payload(
            mitigates=[{"technique": tech_id}],
            lifecycle_phases=[],
            categories=[],
        )
        resp = client.post(f"/{ATLAS_DATA_VERSION}/mitigations/", json=payload)
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Entities
# ---------------------------------------------------------------------------


class TestEntities:
    def test_create_entity_with_fields(self, client: TestClient) -> None:
        resp = client.post(
            f"/{ATLAS_DATA_VERSION}/entities/",
            json=entity_payload(
                associated_entities=[{"name": "Fancy Bear"}, {"name": "Forest Blizzard"}],
                references=[
                    {
                        "id": "entity-ref",
                        "title": "Entity reference",
                        "url": "https://example.com/entity",
                    }
                ],
                attack_reference={
                    "id": "G0007",
                    "url": "https://attack.mitre.org/groups/G0007/",
                },
            ),
        )

        assert resp.status_code == 201
        body = resp.json()
        assert body["id"] == "AML.E0001"
        assert body["object-type"] == "entity"
        assert body["entity-type"] == "Activity Cluster"
        assert body["associated-entities"] == [
            {"name": "Fancy Bear", "description": None},
            {"name": "Forest Blizzard", "description": None},
        ]
        assert body["attack-reference"]["id"] == "G0007"
        assert body["uses"] == []

    def test_entity_crud_and_uses_replacement(
        self, client: TestClient, db: Session
    ) -> None:
        tactic_id = create_tactic(client)
        technique_id = create_technique(client, tactic_id, maturity="Demonstrated")
        software_id = create_software(
            client,
            implements=[{"technique": technique_id, "description": "Implements"}],
        )
        create_resp = client.post(
            f"/{ATLAS_DATA_VERSION}/entities/",
            json=entity_payload(
                entity_type="Team",
                uses=[
                    {
                        "technique": technique_id,
                        "activity_purpose": "Security Evaluation",
                        "description": "Observed behavior",
                    },
                    {"software": software_id, "description": "Operated software"},
                ],
            ),
        )
        assert create_resp.status_code == 201
        entity_id = create_resp.json()["id"]
        assert {
            relationship.get("technique") or relationship.get("software")
            for relationship in create_resp.json()["uses"]
        } == {technique_id, software_id}
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{technique_id}").json()[
                "maturity"
            ]
            == "Demonstrated"
        )

        get_resp = client.get(f"/{ATLAS_DATA_VERSION}/entities/{entity_id}")
        assert get_resp.status_code == 200
        assert {
            relationship.get("technique") or relationship.get("software")
            for relationship in get_resp.json()["uses"]
        } == {technique_id, software_id}
        assert len(client.get(f"/{ATLAS_DATA_VERSION}/entities/").json()) == 1

        update_resp = client.put(
            f"/{ATLAS_DATA_VERSION}/entities/{entity_id}",
            json=entity_payload(
                name="Updated Entity",
                entity_type="Organization",
                associated_entities=[{"name": "Research Unit"}],
                uses=[
                    {
                        "technique": technique_id,
                        "activity_purpose": "Adversarial Operation",
                        "description": "Updated behavior",
                    },
                    {"software": software_id, "description": "Tested software"},
                ],
            ),
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["name"] == "Updated Entity"
        assert update_resp.json()["entity-type"] == "Organization"
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{technique_id}").json()[
                "maturity"
            ]
            == "Demonstrated"
        )

        replace_resp = client.put(
            f"/{ATLAS_DATA_VERSION}/entities/{entity_id}",
            json=entity_payload(
                name="Updated Entity",
                entity_type="Team",
                associated_entities=[{"name": "Research Unit"}],
                uses=[{"software": software_id, "description": "Tested software"}],
            ),
        )
        assert replace_resp.status_code == 200
        assert replace_resp.json()["uses"] == [
            {"software": software_id, "description": "Tested software"}
        ]
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{technique_id}").json()[
                "maturity"
            ]
            == "Demonstrated"
        )

        relationships = (
            db.query(models.Relationship)
            .filter(
                models.Relationship.source == entity_id,
                models.Relationship.relationship_type == AtlasRelationshipType.USES,
            )
            .all()
        )
        assert [relationship.target for relationship in relationships] == [software_id]

        delete_resp = client.delete(f"/{ATLAS_DATA_VERSION}/entities/{entity_id}")
        assert delete_resp.status_code == 200
        assert client.get(f"/{ATLAS_DATA_VERSION}/entities/{entity_id}").status_code == 404
        assert (
            db.query(models.Relationship)
            .filter(models.Relationship.source == entity_id)
            .count()
            == 0
        )

    @pytest.mark.parametrize(
        "purpose", ["Adversarial Operation", "Unintended Consequence"]
    )
    def test_activity_purpose_and_entity_type_preserve_maturity(
        self, client: TestClient, purpose: str
    ) -> None:
        tactic_id = create_tactic(client)
        technique_id = create_technique(client, tactic_id)
        entity_id = create_entity(
            client,
            entity_type="Team",
            uses=[
                {
                    "technique": technique_id,
                    "activity_purpose": "Security Evaluation",
                }
            ],
        )
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{technique_id}").json()[
                "maturity"
            ]
            == "Feasible"
        )

        type_update = client.put(
            f"/{ATLAS_DATA_VERSION}/entities/{entity_id}",
            json=entity_payload(
                entity_type="Organization",
                uses=[
                    {
                        "technique": technique_id,
                        "activity_purpose": "Security Evaluation",
                    }
                ],
            ),
        )
        assert type_update.status_code == 200
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{technique_id}").json()[
                "maturity"
            ]
            == "Feasible"
        )

        purpose_update = client.put(
            f"/{ATLAS_DATA_VERSION}/entities/{entity_id}",
            json=entity_payload(
                entity_type="Organization",
                uses=[
                    {
                        "technique": technique_id,
                        "activity_purpose": purpose,
                    }
                ],
            ),
        )
        assert purpose_update.status_code == 200
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{technique_id}").json()[
                "maturity"
            ]
            == "Feasible"
        )

    def test_entity_ids_are_scoped_by_version(self, client: TestClient) -> None:
        assert create_entity(client) == "AML.E0001"
        assert create_entity(client, name="Second Entity") == "AML.E0002"
        assert (
            client.post(
                "/versions",
                json={
                    "new_version": "2026.06",
                    "collection": {"name": "Test", "description": "Test"},
                },
            ).status_code
            == 201
        )
        assert create_entity(client, version="2026.06") == "AML.E0001"

    def test_entity_create_rolls_back_invalid_uses(self, client: TestClient) -> None:
        missing_resp = client.post(
            f"/{ATLAS_DATA_VERSION}/entities/",
            json=entity_payload(uses=[{"technique": "AML.T9999"}]),
        )
        assert missing_resp.status_code == 409
        assert client.get(f"/{ATLAS_DATA_VERSION}/entities/").json() == []

    def test_entity_create_rolls_back_duplicate_uses(self, client: TestClient) -> None:
        tactic_id = create_tactic(client)
        technique_id = create_technique(client, tactic_id)
        duplicate_resp = client.post(
            f"/{ATLAS_DATA_VERSION}/entities/",
            json=entity_payload(
                uses=[
                    {"technique": technique_id},
                    {"technique": technique_id, "description": "Duplicate"},
                ]
            ),
        )
        assert duplicate_resp.status_code == 409
        assert client.get(f"/{ATLAS_DATA_VERSION}/entities/").json() == []

    def test_entity_update_rolls_back_on_relationship_failure(
        self,
    ) -> None:
        engine = create_engine("sqlite:///:memory:")

        @event.listens_for(engine, "connect")
        def set_pragma(dbapi_connection: Any, connection_record: Any) -> None:
            if isinstance(dbapi_connection, sqlite3.Connection):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        Base.metadata.create_all(bind=engine)
        with Session(engine) as session:
            session.add(models.Version(version=ATLAS_DATA_VERSION))
            session.commit()
            db_entity = services.entities.create(
                session,
                schemas.EntityInput.model_validate(entity_payload(name="Original Entity")),
                ATLAS_DATA_VERSION,
            )
            with pytest.raises(HTTPException) as exc_info:
                services.entities.update(
                    session,
                    db_entity.id,
                    ATLAS_DATA_VERSION,
                    schemas.EntityInput.model_validate(
                        entity_payload(
                            name="Invalid Update",
                            uses=[{"software": "AML.S9999"}],
                        )
                    ),
                )
            assert exc_info.value.status_code == 409

            stored = services.entities.get_one(session, db_entity.id, ATLAS_DATA_VERSION)
            assert stored.name == "Original Entity"
            assert stored.source_relationships == []
        engine.dispose()

    def test_entity_input_rejects_unknown_fields(self, client: TestClient) -> None:
        resp = client.post(
            f"/{ATLAS_DATA_VERSION}/entities/",
            json=entity_payload(unsupported=["Alias"]),
        )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Software
# ---------------------------------------------------------------------------


class TestSoftware:
    def test_software_crud_implements_and_maturity_boundary(
        self, client: TestClient, db: Session
    ) -> None:
        tactic_id = create_tactic(client)
        technique_a = create_technique(client, tactic_id, name="Technique A")
        technique_b = create_technique(client, tactic_id, name="Technique B")
        software_id = create_software(
            client,
            references=[
                {
                    "id": "software-ref",
                    "title": "Software reference",
                    "url": "https://example.com/software",
                }
            ],
            attack_reference={
                "id": "S9035",
                "url": "https://attack.mitre.org/software/S9035/",
            },
            implements=[{"technique": technique_a, "description": "Implements"}],
        )

        body = client.get(f"/{ATLAS_DATA_VERSION}/software/{software_id}").json()
        assert body["id"] == "AML.S0001"
        assert body["object-type"] == "software"
        assert body["software-type"] == "Malware"
        assert body["attack-reference"]["id"] == "S9035"
        assert body["implements"] == [
            {"technique": technique_a, "description": "Implements"}
        ]
        assert len(client.get(f"/{ATLAS_DATA_VERSION}/software/").json()) == 1
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{technique_a}").json()[
                "maturity"
            ]
            == "Feasible"
        )

        update_resp = client.put(
            f"/{ATLAS_DATA_VERSION}/software/{software_id}",
            json=software_payload(
                name="Updated Software",
                software_type="Tool",
                implements=[{"technique": technique_b}],
            ),
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["software-type"] == "Tool"
        assert update_resp.json()["implements"] == [
            {"technique": technique_b, "description": None}
        ]
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{technique_b}").json()[
                "maturity"
            ]
            == "Feasible"
        )

        entity_id = create_entity(client, uses=[{"software": software_id}])
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{technique_b}").json()[
                "maturity"
            ]
            == "Feasible"
        )

        delete_resp = client.delete(f"/{ATLAS_DATA_VERSION}/software/{software_id}")
        assert delete_resp.status_code == 200
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/software/{software_id}").status_code
            == 404
        )
        assert (
            db.query(models.Relationship)
            .filter(models.Relationship.source == software_id)
            .count()
            == 0
        )
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/entities/{entity_id}").json()["uses"] == []
        )

    def test_software_ids_are_scoped_by_version(self, client: TestClient) -> None:
        assert create_software(client) == "AML.S0001"
        assert create_software(client, name="Second Software") == "AML.S0002"
        assert (
            client.post(
                "/versions",
                json={
                    "new_version": "2026.06",
                    "collection": {"name": "Test", "description": "Test"},
                },
            ).status_code
            == 201
        )
        assert create_software(client, version="2026.06") == "AML.S0001"

    def test_software_create_rolls_back_invalid_implements(
        self, client: TestClient
    ) -> None:
        missing_resp = client.post(
            f"/{ATLAS_DATA_VERSION}/software/",
            json=software_payload(implements=[{"technique": "AML.T9999"}]),
        )
        assert missing_resp.status_code == 409
        assert client.get(f"/{ATLAS_DATA_VERSION}/software/").json() == []

    def test_software_create_rolls_back_duplicate_implements(
        self, client: TestClient
    ) -> None:
        tactic_id = create_tactic(client)
        technique_id = create_technique(client, tactic_id)
        duplicate_resp = client.post(
            f"/{ATLAS_DATA_VERSION}/software/",
            json=software_payload(
                implements=[
                    {"technique": technique_id},
                    {"technique": technique_id, "description": "Duplicate"},
                ]
            ),
        )
        assert duplicate_resp.status_code == 409
        assert client.get(f"/{ATLAS_DATA_VERSION}/software/").json() == []


# ---------------------------------------------------------------------------
# Case Studies
# ---------------------------------------------------------------------------


class TestCaseStudies:
    def test_date_range_create_update_export(
        self, client: TestClient, db: Session,
        seed_collection_and_matrix: tuple[str, str],
    ) -> None:
        tactic_id = create_tactic(client)
        technique_id = create_technique(client, tactic_id)
        payload = case_study_payload(attack_chain=[
            dict(technique=technique_id, tactic=tactic_id, step_id="S01")
        ])
        response = client.post(f"/{ATLAS_DATA_VERSION}/case-studies/", json=payload)
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["start-date"] == body["end-date"] == payload["date"]
        assert body["start-date-granularity"] == body["end-date-granularity"] == "Day"
        assert "date" not in body and "date-granularity" not in body
        case_id = body["id"]
        url = f"/{ATLAS_DATA_VERSION}/case-studies/{case_id}"
        payload.pop("date")
        payload.pop("date_granularity")
        payload.update({"start-date": "2024-02", "start-date-granularity": "Month"})
        for end_fields in [
            {},
            {"end-date": "2025-03-15", "end-date-granularity": "Day"},
            {},
        ]:
            response = client.put(url, json={**payload, **end_fields})
            assert response.status_code == 200, response.text
            assert response.json()["start-date"] == "2024-02-01"
            assert response.json()["end-date"] == end_fields.get("end-date")
            assert client.get(url).json() == response.json()
            db.expire_all()
            stored = db.get(models.CaseStudy, (case_id, ATLAS_DATA_VERSION))
            assert (stored.end_date is None) == (not end_fields)
            exported_response = client.get(f"/versions/{ATLAS_DATA_VERSION}/data")
            assert exported_response.status_code == 200
            exported = yaml.safe_load(exported_response.content)
            exported_case = exported["case-studies"][case_id]
            assert exported_case["start-date"] == "2024-02-01"
            assert exported_case.get("end-date") == end_fields.get("end-date")
            assert ("end-date" in exported_case) == bool(end_fields)
            assert "date" not in exported_case
            assert schemas.AtlasExport.model_validate(exported).case_studies[case_id].start_date == stored.start_date
        response = client.put(url, json={
            **payload, "end-date": "2023", "end-date-granularity": "Year"
        })
        assert response.status_code == 422
        assert client.get(url).json()["end-date"] is None

    def test_create_case_study(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_id = create_technique(client, t1_id)
        payload = case_study_payload(
            attack_chain=[
                dict(technique=tech_id, tactic=t1_id, step_id="S01", leads_to=["S02"])
            ],
        )
        resp = client.post(f"/{ATLAS_DATA_VERSION}/case-studies/", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert body["id"] == "AML.CS0001"
        assert body["type"] == "Incident"
        assert body["object-type"] == "case-study"

    def test_get_case_study_by_id(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_id = create_technique(client, t1_id)
        payload = case_study_payload(
            attack_chain=[
                dict(technique=tech_id, tactic=t1_id, step_id="S01", leads_to=["S02"])
            ],
        )
        resp = client.post(f"/{ATLAS_DATA_VERSION}/case-studies/", json=payload)
        cs_id = resp.json()["id"]
        resp = client.get(f"/{ATLAS_DATA_VERSION}/case-studies/{cs_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == cs_id

    def test_get_all_case_studies(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_id = create_technique(client, t1_id)
        payload = case_study_payload(
            attack_chain=[
                dict(technique=tech_id, tactic=t1_id, step_id="S01", leads_to=["S02"])
            ],
        )
        client.post(f"/{ATLAS_DATA_VERSION}/case-studies/", json=payload)
        client.post(
            f"/{ATLAS_DATA_VERSION}/case-studies/",
            json={**payload, "name": "Case Study 2"},
        )
        resp = client.get(f"/{ATLAS_DATA_VERSION}/case-studies/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_update_case_study(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_id = create_technique(client, t1_id)
        payload = case_study_payload(
            attack_chain=[
                dict(technique=tech_id, tactic=t1_id, step_id="S01", leads_to=["S02"])
            ],
        )
        resp = client.post(f"/{ATLAS_DATA_VERSION}/case-studies/", json=payload)
        cs_id = resp.json()["id"]
        updated_payload = case_study_payload(
            name="Updated CS",
            attack_chain=[
                dict(technique=tech_id, tactic=t1_id, step_id="S01", leads_to=["S02"])
            ],
        )
        resp = client.put(
            f"/{ATLAS_DATA_VERSION}/case-studies/{cs_id}", json=updated_payload
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated CS"

    def test_delete_case_study(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_id = create_technique(client, t1_id)
        payload = case_study_payload(
            attack_chain=[
                dict(technique=tech_id, tactic=t1_id, step_id="S01", leads_to=["S02"])
            ],
        )
        resp = client.post(f"/{ATLAS_DATA_VERSION}/case-studies/", json=payload)
        cs_id = resp.json()["id"]
        resp = client.delete(f"/{ATLAS_DATA_VERSION}/case-studies/{cs_id}")
        assert resp.status_code == 200
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/case-studies/{cs_id}").status_code == 404
        )

    def test_case_study_attributed_to_create_update_and_entity_cleanup(
        self, client: TestClient
    ) -> None:
        tactic_id = create_tactic(client)
        technique_id = create_technique(client, tactic_id)
        attribution_technique = create_technique(
            client, tactic_id, name="Attribution Technique", maturity="Demonstrated"
        )
        entity_a = create_entity(
            client,
            name="Entity A",
            entity_type="Team",
            uses=[
                {
                    "technique": attribution_technique,
                    "activity_purpose": "Security Evaluation",
                }
            ],
        )
        entity_b = create_entity(client, name="Entity B")
        create_resp = client.post(
            f"/{ATLAS_DATA_VERSION}/case-studies/",
            json=case_study_payload(
                actor="Original attribution text",
                attack_chain=[
                    {
                        "technique": technique_id,
                        "tactic": tactic_id,
                        "step_id": "S01",
                        "leads_to": [],
                    }
                ],
                attributed_to=[
                    {"entity": entity_a, "description": "Primary attribution"},
                    {"entity": entity_b},
                ],
            ),
        )
        assert create_resp.status_code == 201
        case_study_id = create_resp.json()["id"]
        assert {
            attribution["entity"] for attribution in create_resp.json()["attributed-to"]
        } == {entity_a, entity_b}
        assert (
            client.get(
                f"/{ATLAS_DATA_VERSION}/techniques/{attribution_technique}"
            ).json()["maturity"]
            == "Demonstrated"
        )

        update_resp = client.put(
            f"/{ATLAS_DATA_VERSION}/case-studies/{case_study_id}",
            json=case_study_payload(
                actor="Original attribution text",
                attack_chain=[
                    {
                        "technique": technique_id,
                        "tactic": tactic_id,
                        "step_id": "S01",
                        "leads_to": [],
                    }
                ],
                attributed_to=[
                    {"entity": entity_b, "description": "Updated attribution"}
                ],
            ),
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["actor"] == "Original attribution text"
        assert update_resp.json()["attributed-to"] == [
            {
                "entity": entity_b,
                "activity-purpose": "Adversarial Operation",
                "description": "Updated attribution",
            }
        ]
        assert (
            client.get(
                f"/{ATLAS_DATA_VERSION}/techniques/{attribution_technique}"
            ).json()["maturity"]
            == "Demonstrated"
        )

        delete_entity_resp = client.delete(f"/{ATLAS_DATA_VERSION}/entities/{entity_b}")
        assert delete_entity_resp.status_code == 200
        stored_case_study = client.get(
            f"/{ATLAS_DATA_VERSION}/case-studies/{case_study_id}"
        )
        assert stored_case_study.status_code == 200
        assert stored_case_study.json()["attributed-to"] == []
        assert stored_case_study.json()["actor"] == "Original attribution text"
        assert (
            client.get(
                f"/{ATLAS_DATA_VERSION}/techniques/{attribution_technique}"
            ).json()["maturity"]
            == "Demonstrated"
        )

    def test_case_study_attributed_to_rejects_missing_entity(
        self, client: TestClient
    ) -> None:
        tactic_id = create_tactic(client)
        technique_id = create_technique(client, tactic_id)
        attack_chain = [
            {
                "technique": technique_id,
                "tactic": tactic_id,
                "step_id": "S01",
                "leads_to": [],
            }
        ]

        missing_resp = client.post(
            f"/{ATLAS_DATA_VERSION}/case-studies/",
            json=case_study_payload(
                attack_chain=attack_chain,
                attributed_to=[{"entity": "AML.E9999"}],
            ),
        )
        assert missing_resp.status_code == 409
        assert client.get(f"/{ATLAS_DATA_VERSION}/case-studies/").json() == []

    def test_case_study_attributed_to_rejects_cross_version_entity(
        self, client: TestClient
    ) -> None:
        tactic_id = create_tactic(client)
        technique_id = create_technique(client, tactic_id)
        assert (
            client.post(
                "/versions",
                json={
                    "new_version": "2026.06",
                    "collection": {"name": "Test", "description": "Test"},
                },
            ).status_code
            == 201
        )
        other_version_entity = create_entity(client, version="2026.06")
        cross_version_resp = client.post(
            f"/{ATLAS_DATA_VERSION}/case-studies/",
            json=case_study_payload(
                attack_chain=[
                    {
                        "technique": technique_id,
                        "tactic": tactic_id,
                        "step_id": "S01",
                        "leads_to": [],
                    }
                ],
                attributed_to=[{"entity": other_version_entity}],
            ),
        )
        assert cross_version_resp.status_code == 409
        assert client.get(f"/{ATLAS_DATA_VERSION}/case-studies/").json() == []

    def test_case_study_attributed_to_rejects_duplicate_entity(
        self, client: TestClient
    ) -> None:
        tactic_id = create_tactic(client)
        technique_id = create_technique(client, tactic_id)
        entity_id = create_entity(client)
        duplicate_resp = client.post(
            f"/{ATLAS_DATA_VERSION}/case-studies/",
            json=case_study_payload(
                attack_chain=[
                    {
                        "technique": technique_id,
                        "tactic": tactic_id,
                        "step_id": "S01",
                        "leads_to": [],
                    }
                ],
                attributed_to=[
                    {"entity": entity_id},
                    {"entity": entity_id, "description": "Duplicate"},
                ],
            ),
        )
        assert duplicate_resp.status_code == 409
        assert client.get(f"/{ATLAS_DATA_VERSION}/case-studies/").json() == []

    def test_case_study_attributed_to_rejects_software(
        self, client: TestClient
    ) -> None:
        tactic_id = create_tactic(client)
        technique_id = create_technique(client, tactic_id)
        software_id = create_software(client)
        resp = client.post(
            f"/{ATLAS_DATA_VERSION}/case-studies/",
            json=case_study_payload(
                attack_chain=[
                    {
                        "technique": technique_id,
                        "tactic": tactic_id,
                        "step_id": "S01",
                        "leads_to": [],
                    }
                ],
                attributed_to=[{"entity": software_id}],
            ),
        )
        assert resp.status_code == 422

    def test_update_case_study_preserves_child_and_parent_maturity(
        self, client
    ) -> None:
        tactic_id = create_tactic(client)
        parent_id = create_technique(client, tactic_id, maturity="Realized")
        child_id = client.post(
            f"/{ATLAS_DATA_VERSION}/techniques/",
            json=technique_payload(
                tactics=[{"tactic": tactic_id}],
                name="Child",
                maturity="Realized",
                specializes={"technique": parent_id},
            ),
        ).json()["id"]

        create_resp = client.post(
            f"/{ATLAS_DATA_VERSION}/case-studies/",
            json=case_study_payload(
                attack_chain=[
                    dict(
                        technique=child_id,
                        tactic=tactic_id,
                        step_id="S01",
                        leads_to=["S02"],
                    )
                ],
            ),
        )
        assert create_resp.status_code == 201
        case_study_id = create_resp.json()["id"]

        parent_before = client.get(f"/{ATLAS_DATA_VERSION}/techniques/{parent_id}")
        child_before = client.get(f"/{ATLAS_DATA_VERSION}/techniques/{child_id}")
        assert parent_before.status_code == 200
        assert child_before.status_code == 200
        assert parent_before.json()["maturity"] == "Realized"
        assert child_before.json()["maturity"] == "Realized"

        update_resp = client.put(
            f"/{ATLAS_DATA_VERSION}/case-studies/{case_study_id}",
            json=case_study_payload(
                type="Exercise",
                reporter=None,
                attack_chain=[
                    dict(
                        technique=child_id,
                        tactic=tactic_id,
                        step_id="S01",
                        leads_to=["S02"],
                    )
                ],
            ),
        )
        assert update_resp.status_code == 200

        parent_after = client.get(f"/{ATLAS_DATA_VERSION}/techniques/{parent_id}")
        child_after = client.get(f"/{ATLAS_DATA_VERSION}/techniques/{child_id}")
        assert parent_after.status_code == 200
        assert child_after.status_code == 200
        assert parent_after.json()["maturity"] == "Realized"
        assert child_after.json()["maturity"] == "Realized"

        replacement_target = create_technique(
            client, tactic_id, name="Replacement Target"
        )
        entity_id = create_entity(
            client,
            entity_type="Organization",
            uses=[{"technique": child_id}],
        )
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{parent_id}").json()[
                "maturity"
            ]
            == "Realized"
        )

        entity_update = client.put(
            f"/{ATLAS_DATA_VERSION}/entities/{entity_id}",
            json=entity_payload(
                entity_type="Organization",
                uses=[{"technique": replacement_target}],
            ),
        )
        assert entity_update.status_code == 200
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{parent_id}").json()[
                "maturity"
            ]
            == "Realized"
        )
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{child_id}").json()[
                "maturity"
            ]
            == "Realized"
        )
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{replacement_target}").json()[
                "maturity"
            ]
            == "Feasible"
        )

    def test_delete_case_studies_preserves_parent_across_multiple_children(
        self, client: TestClient
    ) -> None:
        tactic_id = create_tactic(client)
        parent_id = create_technique(client, tactic_id, maturity="Realized")
        child_a = client.post(
            f"/{ATLAS_DATA_VERSION}/techniques/",
            json=technique_payload(
                tactics=[{"tactic": tactic_id}],
                name="Child A",
                maturity="Realized",
                specializes={"technique": parent_id},
            ),
        ).json()["id"]
        child_b = client.post(
            f"/{ATLAS_DATA_VERSION}/techniques/",
            json=technique_payload(
                tactics=[{"tactic": tactic_id}],
                name="Child B",
                maturity="Demonstrated",
                specializes={"technique": parent_id},
            ),
        ).json()["id"]

        cs_incident = client.post(
            f"/{ATLAS_DATA_VERSION}/case-studies/",
            json=case_study_payload(
                name="Incident CS",
                type="Incident",
                attack_chain=[
                    dict(
                        technique=child_a,
                        tactic=tactic_id,
                        step_id="S01",
                        leads_to=["S02"],
                    )
                ],
            ),
        )
        cs_exercise = client.post(
            f"/{ATLAS_DATA_VERSION}/case-studies/",
            json=case_study_payload(
                name="Exercise CS",
                type="Exercise",
                reporter=None,
                attack_chain=[
                    dict(
                        technique=child_b,
                        tactic=tactic_id,
                        step_id="S01",
                        leads_to=["S02"],
                    )
                ],
            ),
        )
        assert cs_incident.status_code == 201
        assert cs_exercise.status_code == 201
        research_entity = create_entity(
            client,
            name="Research Entity",
            entity_type="Team",
            uses=[
                {
                    "technique": child_a,
                    "activity_purpose": "Security Evaluation",
                }
            ],
        )
        adversary_entity = create_entity(
            client,
            name="Adversary Entity",
            entity_type="Activity Cluster",
            uses=[{"technique": child_b}],
        )

        parent_initial = client.get(f"/{ATLAS_DATA_VERSION}/techniques/{parent_id}")
        assert parent_initial.status_code == 200
        assert parent_initial.json()["maturity"] == "Realized"

        delete_incident = client.delete(
            f"/{ATLAS_DATA_VERSION}/case-studies/{cs_incident.json()['id']}"
        )
        assert delete_incident.status_code == 200

        parent_after_first_delete = client.get(
            f"/{ATLAS_DATA_VERSION}/techniques/{parent_id}"
        )
        assert parent_after_first_delete.status_code == 200
        assert parent_after_first_delete.json()["maturity"] == "Realized"

        delete_adversary = client.delete(
            f"/{ATLAS_DATA_VERSION}/entities/{adversary_entity}"
        )
        assert delete_adversary.status_code == 200
        assert (
            client.get(f"/{ATLAS_DATA_VERSION}/techniques/{parent_id}").json()[
                "maturity"
            ]
            == "Realized"
        )

        delete_exercise = client.delete(
            f"/{ATLAS_DATA_VERSION}/case-studies/{cs_exercise.json()['id']}"
        )
        assert delete_exercise.status_code == 200

        parent_after_second_delete = client.get(
            f"/{ATLAS_DATA_VERSION}/techniques/{parent_id}"
        )
        assert parent_after_second_delete.status_code == 200
        assert parent_after_second_delete.json()["maturity"] == "Realized"

        delete_research = client.delete(
            f"/{ATLAS_DATA_VERSION}/entities/{research_entity}"
        )
        assert delete_research.status_code == 200
        parent_after_all_evidence = client.get(
            f"/{ATLAS_DATA_VERSION}/techniques/{parent_id}"
        )
        assert parent_after_all_evidence.status_code == 200
        assert parent_after_all_evidence.json()["maturity"] == "Realized"


# ---------------------------------------------------------------------------
# Relationships
# ---------------------------------------------------------------------------


class TestRelationships:
    def test_technique_includes_tactics(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        t2_id = create_tactic(client, name="Tactic 2")
        tech_id = create_technique(
            client,
            t1_id,
            tactics=[{"tactic": t1_id}, {"tactic": t2_id}],
        )
        resp = client.get(f"/{ATLAS_DATA_VERSION}/techniques/{tech_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["tactics"]) == 2
        targets = {r["tactic"] for r in body["tactics"]}
        assert targets == {t1_id, t2_id}

    def test_subtechnique_includes_parent(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        parent_id = create_technique(client, t1_id)
        sub_id = create_technique(
            client,
            t1_id,
            name="Sub",
            specializes={"technique": parent_id},
        )
        resp = client.get(f"/{ATLAS_DATA_VERSION}/techniques/{sub_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["specializes"] is not None
        assert body["specializes"]["technique"] == parent_id

    def test_mitigation_includes_mitigates(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_a = create_technique(client, t1_id)
        tech_b = create_technique(client, t1_id, name="Technique 2")
        payload = mitigation_payload(
            mitigates=[{"technique": tech_a}, {"technique": tech_b}],
        )
        resp = client.post(f"/{ATLAS_DATA_VERSION}/mitigations/", json=payload)
        mid = resp.json()["id"]
        resp = client.get(f"/{ATLAS_DATA_VERSION}/mitigations/{mid}")
        mitigates = resp.json()["mitigates"]
        targets = {r["technique"] for r in mitigates}
        assert targets == {tech_a, tech_b}

    def test_delete_object_removes_relationships(self, client: TestClient) -> None:
        t1_id = create_tactic(client)
        tech_id = create_technique(client, t1_id)
        payload = mitigation_payload(mitigates=[{"technique": tech_id}])
        resp = client.post(f"/{ATLAS_DATA_VERSION}/mitigations/", json=payload)
        mid = resp.json()["id"]
        client.delete(f"/{ATLAS_DATA_VERSION}/techniques/{tech_id}")
        resp = client.get(f"/{ATLAS_DATA_VERSION}/mitigations/{mid}")
        assert resp.status_code == 200
        assert resp.json()["mitigates"] == []


# ---------------------------------------------------------------------------
# Collection & Matrix
# ---------------------------------------------------------------------------


class TestCollectionAndMatrix:
    def test_get_collection_not_found(self, client: TestClient) -> None:
        resp = client.get(f"/{ATLAS_DATA_VERSION}/collection/")
        assert resp.status_code == 404

    def test_get_collection(self, client: TestClient, seed_collection: str) -> None:
        resp = client.get(f"/{ATLAS_DATA_VERSION}/collection/")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == "ATLAS-collection"
        assert body["version"] == ATLAS_DATA_VERSION

    def test_update_collection(self, client: TestClient, seed_collection: str) -> None:
        resp = client.put(
            f"/{ATLAS_DATA_VERSION}/collection/",
            json={
                "name": "Updated Collection",
                "description": "Updated",
                "references": [],
                "created_date": "2024-01-01",
                "modified_date": "2024-02-02",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["version"] == ATLAS_DATA_VERSION
        assert resp.json()["name"] == "Updated Collection"
        assert resp.json()["created-date"] == "2024-01-01"
        assert resp.json()["modified-date"] == "2024-02-02"

    def test_get_matrix_not_found(self, client: TestClient) -> None:
        resp = client.get(f"/{ATLAS_DATA_VERSION}/matrix/")
        assert resp.status_code == 404

    def test_get_matrix(
        self, client: TestClient, db: Session, seed_matrix: str
    ) -> None:
        resp = client.post(f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload())
        t1_id = resp.json()["id"]
        add_matrix_sequence(db, t1_id, position=1)
        db.commit()

        resp = client.get(f"/{ATLAS_DATA_VERSION}/matrix/")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == "ATLAS-matrix"
        assert len(body["sequences"]) == 1
        assert body["sequences"][0]["tactic"] == t1_id
        assert body["sequences"][0]["position"] == 1

    def test_get_matrix_sequences_sorted_by_position(
        self, client: TestClient, db: Session, seed_matrix: str
    ) -> None:
        t1_id = client.post(
            f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload(name="Tactic A")
        ).json()["id"]
        t2_id = client.post(
            f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload(name="Tactic B")
        ).json()["id"]

        add_matrix_sequence(db, t1_id, position=2)
        add_matrix_sequence(db, t2_id, position=1)
        db.commit()

        resp = client.get(f"/{ATLAS_DATA_VERSION}/matrix/")
        assert resp.status_code == 200
        body = resp.json()
        assert [s["tactic"] for s in body["sequences"]] == [t2_id, t1_id]
        assert [s["position"] for s in body["sequences"]] == [1, 2]

    def test_update_matrix(self, client: TestClient, seed_matrix: str) -> None:
        t1_id = client.post(
            f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload(name="Tactic A")
        ).json()["id"]
        t2_id = client.post(
            f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload(name="Tactic B")
        ).json()["id"]

        resp = client.put(
            f"/{ATLAS_DATA_VERSION}/matrix/",
            json={
                "name": "Updated Matrix",
                "description": "Updated matrix",
                "references": [],
                "created_date": "2024-03-01",
                "modified_date": "2024-03-02",
                "sequences": [
                    {"tactic": t2_id, "position": 1, "description": "First"},
                    {"tactic": t1_id, "position": 2, "description": "Second"},
                ],
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["name"] == "Updated Matrix"
        assert body["created-date"] == "2024-03-01"
        assert body["modified-date"] == "2024-03-02"
        assert [s["tactic"] for s in body["sequences"]] == [t2_id, t1_id]
        assert [s["position"] for s in body["sequences"]] == [1, 2]

    def test_update_matrix_extra_field_forbidden(
        self, client: TestClient, seed_matrix: str
    ) -> None:
        tactic_id = client.post(
            f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload(name="Tactic A")
        ).json()["id"]

        resp = client.put(
            f"/{ATLAS_DATA_VERSION}/matrix/",
            json={
                "name": "Updated Matrix",
                "description": "Updated matrix",
                "references": [],
                "created_date": "2024-03-01",
                "modified_date": "2024-03-02",
                "sequences": [
                    {"tactic": tactic_id, "position": 1, "description": "First"}
                ],
                "unknown_field": "should not be allowed",
            },
        )
        assert resp.status_code == 422

    def test_update_matrix_nested_extra_field_forbidden(
        self, client: TestClient, seed_matrix: str
    ) -> None:
        tactic_id = client.post(
            f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload(name="Tactic A")
        ).json()["id"]

        resp = client.put(
            f"/{ATLAS_DATA_VERSION}/matrix/",
            json={
                "name": "Updated Matrix",
                "description": "Updated matrix",
                "references": [],
                "created_date": "2024-03-01",
                "modified_date": "2024-03-02",
                "sequences": [
                    {
                        "tactic": tactic_id,
                        "position": 1,
                        "description": "First",
                        "unknown_nested": "should not be allowed",
                    }
                ],
            },
        )
        assert resp.status_code == 422


class TestVersions:
    @pytest.fixture()
    def registered_versions(self) -> tuple[str, ...]:
        return ()

    @pytest.mark.parametrize(
        "resource,payload_factory",
        [
            ("tactics", tactic_payload),
            ("techniques", technique_payload),
            ("mitigations", mitigation_payload),
            ("case-studies", case_study_payload),
            ("entities", entity_payload),
            ("software", software_payload),
        ],
    )
    def test_create_rejects_missing_version(
        self, client, db, resource, payload_factory
    ):
        response = client.post(f"/missing/{resource}/", json=payload_factory())
        assert response.status_code == 404
        assert response.json()["detail"] == "Version missing not found."
        assert db.query(models.AtlasObject).count() == 0

    def test_list_versions_empty(self, client: TestClient) -> None:
        resp = client.get("/versions")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_versions(self, client: TestClient) -> None:
        resp1 = client.post(
            "/versions",
            json={
                "new_version": "9.0.0",
                "collection": {
                    "name": "Collection 9.0.0",
                    "description": "First",
                    "references": [],
                },
            },
        )
        assert resp1.status_code == 201

        resp2 = client.post(
            "/versions",
            json={
                "new_version": "9.0.1",
                "base_version": "9.0.0",
            },
        )
        assert resp2.status_code == 201

        resp = client.get("/versions")
        assert resp.status_code == 200
        body = resp.json()
        assert [entry["version"] for entry in body] == ["9.0.0", "9.0.1"]
        assert body[0]["base-version"] is None
        assert body[1]["base-version"] == "9.0.0"

    def test_create_version_with_collection_reference(self, client: TestClient) -> None:
        response = client.post(
            "/versions",
            json={
                "new_version": "9.0.6",
                "collection": {
                    "name": "Collection 9.0.6",
                    "description": "Reference test",
                    "references": [
                        {
                            "id": "source",
                            "title": "Source",
                            "url": "https://example.com/source",
                        }
                    ],
                },
            },
        )
        assert response.status_code == 201

        collection = client.get("/9.0.6/collection/")
        assert collection.status_code == 200
        assert collection.json()["references"][0]["id"] == "source"

        copied = client.post(
            "/versions",
            json={"new_version": "9.0.7", "base_version": "9.0.6"},
        )
        assert copied.status_code == 201
        copied_collection = client.get("/9.0.7/collection/")
        assert copied_collection.status_code == 200
        assert copied_collection.json()["references"][0]["id"] == "source"

    def test_get_version_success(self, client: TestClient) -> None:
        create_resp = client.post(
            "/versions",
            json={
                "new_version": "9.0.5",
                "collection": {
                    "name": "Collection 9.0.5",
                    "description": "Get version",
                    "references": [],
                },
            },
        )
        assert create_resp.status_code == 201

        resp = client.get("/versions/9.0.5")
        assert resp.status_code == 200
        body = resp.json()
        assert body["version"] == "9.0.5"
        assert body["base-version"] is None

    def test_update_version_metadata_success(self, client: TestClient) -> None:
        create_resp = client.post(
            "/versions",
            json={
                "new_version": "9.0.2",
                "collection": {
                    "name": "Collection 9.0.2",
                    "description": "Update metadata",
                    "references": [],
                },
            },
        )
        assert create_resp.status_code == 201

        patch_resp = client.patch(
            "/versions/9.0.2",
            json={"publish_date": "2026-05-01"},
        )
        assert patch_resp.status_code == 200
        body = patch_resp.json()
        assert body["version"] == "9.0.2"
        assert body["publish-date"] == "2026-05-01"
        assert body["modified-date"]

    def test_update_version_metadata_not_found(self, client: TestClient) -> None:
        resp = client.patch(
            "/versions/9.9.9",
            json={"publish_date": "2026-05-01"},
        )
        assert resp.status_code == 404

    def test_update_version_metadata_invalid_payload(self, client: TestClient) -> None:
        create_resp = client.post(
            "/versions",
            json={
                "new_version": "9.0.3",
                "collection": {
                    "name": "Collection 9.0.3",
                    "description": "Invalid patch",
                    "references": [],
                },
            },
        )
        assert create_resp.status_code == 201

        resp = client.patch(
            "/versions/9.0.3",
            json={"publish_date": "not-a-date"},
        )
        assert resp.status_code == 422

    def test_update_version_metadata_allows_null_publish_date(
        self, client: TestClient
    ) -> None:
        create_resp = client.post(
            "/versions",
            json={
                "new_version": "9.0.4",
                "collection": {
                    "name": "Collection 9.0.4",
                    "description": "Null publish date",
                    "references": [],
                },
            },
        )
        assert create_resp.status_code == 201

        resp = client.patch(
            "/versions/9.0.4",
            json={"publish_date": None},
        )
        assert resp.status_code == 200
        assert resp.json()["publish-date"] is None

    def test_delete_version_not_found(self, client: TestClient) -> None:
        resp = client.delete("/versions/9.9.9")
        assert resp.status_code == 404

    def test_delete_version_blocked_if_referenced_as_base(
        self, client: TestClient
    ) -> None:
        parent_resp = client.post(
            "/versions",
            json={
                "new_version": "9.2.0",
                "collection": {
                    "name": "Parent Collection",
                    "description": "Parent",
                    "references": [],
                },
            },
        )
        assert parent_resp.status_code == 201

        child_resp = client.post(
            "/versions",
            json={"new_version": "9.2.1", "base_version": "9.2.0"},
        )
        assert child_resp.status_code == 201

        del_resp = client.delete("/versions/9.2.0")
        assert del_resp.status_code == 409

    def test_delete_version_removes_all_data(
        self, client: TestClient, db: Session
    ) -> None:
        version = "9.1.0"
        create_resp = client.post(
            "/versions",
            json={
                "new_version": version,
                "collection": {
                    "name": "Test Collection",
                    "description": "Test version",
                    "references": [],
                },
            },
        )
        assert create_resp.status_code == 201

        db.add_all(
            [
                models.Entity(
                    id="AML.E0001",
                    version=version,
                    name="Test Entity",
                    description="Test entity",
                    references=[],
                    entity_type="Activity Cluster",
                    associated_entities=[],
                    attack_reference=None,
                ),
                models.Software(
                    id="AML.S0001",
                    version=version,
                    name="Test Software",
                    description="Test software",
                    references=[],
                    software_type="Malware",
                    attack_reference=None,
                ),
            ]
        )
        db.flush()
        db.add(
            models.Relationship(
                source="AML.E0001",
                target="AML.S0001",
                version=version,
                relationship_type=AtlasRelationshipType.USES,
            )
        )
        db.commit()

        assert db.query(models.AtlasObject).filter_by(version=version).count() == 3
        assert db.query(models.Relationship).filter_by(version=version).count() == 1

        del_resp = client.delete(f"/versions/{version}")
        assert del_resp.status_code == 200

        assert db.query(models.Relationship).filter_by(version=version).count() == 0
        assert db.query(models.Collection).filter_by(version=version).count() == 0
        assert db.query(models.Entity).filter_by(version=version).count() == 0
        assert db.query(models.Software).filter_by(version=version).count() == 0
        assert db.query(models.AtlasObject).filter_by(version=version).count() == 0
        assert db.query(models.Version).filter_by(version=version).count() == 0

        ver_resp = client.get(f"/versions/{version}")
        assert ver_resp.status_code == 404

        coll_resp = client.get(f"/{version}/collection/")
        assert coll_resp.status_code == 404

        data_resp = client.get(f"/versions/{version}/data")
        assert data_resp.status_code == 404

        recreate_resp = client.post(
            "/versions",
            json={
                "new_version": version,
                "collection": {
                    "name": "Recreated Collection",
                    "description": "Recreated version",
                    "references": [],
                },
            },
        )
        assert recreate_resp.status_code == 201
        assert client.get(f"/{version}/collection/").json()["name"] == (
            "Recreated Collection"
        )

    def test_create_copy_version_is_atomic_on_commit_failure(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        base_version = "9.3.0"
        new_version = "9.3.1"

        create_base = client.post(
            "/versions",
            json={
                "new_version": base_version,
                "collection": {
                    "name": "Atomicity Base",
                    "description": "Base",
                    "references": [],
                },
            },
        )
        assert create_base.status_code == 201

        tactic_resp = client.post(f"/{base_version}/tactics/", json=tactic_payload())
        assert tactic_resp.status_code == 201

        original_transactional = versions_service.transactional

        @contextmanager
        def fail_transactional(db):
            try:
                yield
                db.rollback()
                raise HTTPException(status_code=500, detail="simulated commit failure")
            except Exception:
                db.rollback()
                raise

        monkeypatch.setattr(versions_service, "transactional", fail_transactional)

        copy_resp = client.post(
            "/versions",
            json={"new_version": new_version, "base_version": base_version},
        )
        assert copy_resp.status_code == 500

        monkeypatch.setattr(versions_service, "transactional", original_transactional)

        versions_resp = client.get("/versions")
        assert versions_resp.status_code == 200
        assert all(v["version"] != new_version for v in versions_resp.json())

        collection_resp = client.get(f"/{new_version}/collection/")
        assert collection_resp.status_code == 404

        tactics_resp = client.get(f"/{new_version}/tactics/")
        assert tactics_resp.status_code == 200
        assert tactics_resp.json() == []


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    def test_invalid_enum_value(self, client: TestClient) -> None:
        client.post(f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload())
        payload = technique_payload(maturity="InvalidMaturity")
        resp = client.post(f"/{ATLAS_DATA_VERSION}/techniques/", json=payload)
        assert resp.status_code == 422

    def test_invalid_http_url(self, client: TestClient) -> None:
        payload = tactic_payload(
            references=[{"id": "bad", "title": "Bad", "url": "not-a-url"}],
        )
        resp = client.post(f"/{ATLAS_DATA_VERSION}/tactics/", json=payload)
        assert resp.status_code == 422

    def test_relationship_with_nonexistent_target(self, client: TestClient) -> None:
        """FK enforcement prevents referencing non-existent objects."""
        payload = technique_payload(tactics=[{"tactic": "AML.TA9999"}])
        resp = client.post(f"/{ATLAS_DATA_VERSION}/techniques/", json=payload)
        assert resp.status_code in (409, 422, 500)


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


class TestExport:
    def test_export_not_found(self, client: TestClient) -> None:
        resp = client.get("/versions/9.9.9/data")
        assert resp.status_code == 404

    def test_export_empty_collection(
        self, client: TestClient, seed_collection_and_matrix: tuple[str, str]
    ) -> None:
        resp = client.get(f"/versions/{ATLAS_DATA_VERSION}/data")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/x-yaml"

        parsed = yaml.safe_load(resp.content)
        assert parsed["collection"]["id"] == "ATLAS-collection"
        assert parsed["collection"]["version"] == ATLAS_DATA_VERSION
        assert parsed["matrix"]["id"] == "ATLAS-matrix"

    def test_export_round_trip(
        self,
        client: TestClient,
        db: Session,
        seed_collection_and_matrix: tuple[str, str],
    ) -> None:

        tactic_id = client.post(
            f"/{ATLAS_DATA_VERSION}/tactics/",
            json=tactic_payload(
                attack_reference={
                    "id": "TA0001",
                    "url": "https://attack.mitre.org/tactics/TA0001",
                },
            ),
        ).json()["id"]

        technique_id = client.post(
            f"/{ATLAS_DATA_VERSION}/techniques/",
            json=technique_payload(
                tactics=[
                    {"tactic": tactic_id, "description": "occurs in the test tactic"}
                ],
            ),
        ).json()["id"]

        assessed_id = create_technique(
            client, tactic_id, name="Editorial assessment", maturity="Realized"
        )

        software_id = create_software(
            client,
            implements=[{"technique": technique_id, "description": "implements"}],
        )
        entity_id = create_entity(
            client,
            uses=[
                {"technique": technique_id, "description": "observed behavior"},
                {"software": software_id, "description": "operated software"},
            ],
        )

        client.post(
            f"/{ATLAS_DATA_VERSION}/mitigations/",
            json=mitigation_payload(
                mitigates=[
                    {
                        "technique": technique_id,
                        "description": "mitigates the test technique",
                    }
                ],
            ),
        )

        case_study_id = client.post(
            f"/{ATLAS_DATA_VERSION}/case-studies/",
            json=case_study_payload(
                attack_chain=[
                    dict(
                        technique=technique_id,
                        tactic=tactic_id,
                        step_id="S01",
                        leads_to=["S02"],
                    )
                ],
                attributed_to=[{"entity": entity_id, "description": "attributed entity"}],
                reported_by=[{"entity": entity_id, "description": "Published report"}],
            ),
        ).json()["id"]

        add_matrix_sequence(db, tactic_id, position=1, description="matrix has tactic")
        db.commit()

        resp = client.get(f"/versions/{ATLAS_DATA_VERSION}/data")
        assert resp.status_code == 200

        parsed = yaml.safe_load(resp.content)
        assert len(parsed["tactics"]) == 1
        assert len(parsed["techniques"]) == 2
        assert parsed["techniques"][assessed_id]["maturity"] == "Realized"
        assert len(parsed["mitigations"]) == 1
        assert len(parsed["case-studies"]) == 1
        assert list(parsed["entities"]) == [entity_id]
        assert list(parsed["software"]) == [software_id]

        # Techniques should NOT have embedded tactics relationship
        technique_key, technique = next(iter(parsed["techniques"].items()))
        assert "tactics" not in technique
        assert "specializes" not in technique

        # Mitigations should NOT have embedded mitigates relationship
        mitigation_key, mitigation = next(iter(parsed["mitigations"].items()))
        assert "mitigates" not in mitigation

        # Entities and Software should NOT have embedded relationships
        assert "uses" not in parsed["entities"][entity_id]
        assert "implements" not in parsed["software"][software_id]

        # Matrix should NOT have embedded tactics relationship
        matrix = parsed["matrix"]
        assert "tactics" not in matrix

        # All relationships are in the relationships dict
        rels = parsed.get("relationships", {})
        assert technique_id in rels
        assert "achieves" in rels[technique_id]
        assert any(
            r["target"] == tactic_id
            and r.get("description") == "occurs in the test tactic"
            for r in rels[technique_id]["achieves"]
        )
        assert any(
            "mitigates" in type_dict
            and any(
                r.get("description") == "mitigates the test technique"
                for r in type_dict["mitigates"]
            )
            for type_dict in rels.values()
        )
        assert "ATLAS-matrix" in rels
        assert "sequences" in rels["ATLAS-matrix"]
        assert any(
            r.get("description") == "matrix has tactic"
            for r in rels["ATLAS-matrix"]["sequences"]
        )
        assert any(r.get("position") == 1 for r in rels["ATLAS-matrix"]["sequences"])
        assert {entry["target"] for entry in rels[entity_id]["uses"]} == {
            technique_id,
            software_id,
        }
        assert rels[software_id]["implements"][0]["target"] == technique_id
        assert rels[case_study_id]["attributed-to"][0]["target"] == entity_id
        assert rels[case_study_id]["reported-by"][0]["target"] == entity_id
        assert parsed["case-studies"][case_study_id]["reporter"] == "Test Reporter"

        from tools.populate_atlas_db import insert_version_bundle

        insert_version_bundle(db, schemas.AtlasExport.model_validate(parsed), "2026.06")
        db.flush()
        imported = services.techniques.get_one(db, assessed_id, "2026.06")
        assert imported.maturity.value == "Realized"

        db.add(models.Version(version="2026.07", base_version="2026.06"))
        db.flush()
        versions_service.copy(db, "2026.06", "2026.07")
        db.flush()
        copied = services.techniques.get_one(db, assessed_id, "2026.07")
        assert copied.maturity.value == "Realized"

        for version in ("2026.06", "2026.07"):
            stored = services.case_studies.get_one(db, case_study_id, version)
            assert stored.reporter == "Test Reporter"
            reporting = [
                rel for rel in stored.source_relationships
                if rel.relationship_type == AtlasRelationshipType.REPORTED_BY
            ]
            assert [(rel.target, rel.description) for rel in reporting] == [
                (entity_id, "Published report")
            ]

    def test_export_descriptions_and_ordering(
        self,
        client: TestClient,
        db: Session,
        seed_collection_and_matrix: tuple[str, str],
    ) -> None:

        resp1 = client.post(
            f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload(name="Tactic B")
        )
        t2_id = resp1.json()["id"]
        resp2 = client.post(
            f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload(name="Tactic A")
        )
        t1_id = resp2.json()["id"]

        for tid in (t1_id, t2_id):
            add_matrix_sequence(db, tid)
        db.commit()

        resp = client.get(f"/versions/{ATLAS_DATA_VERSION}/data")
        assert resp.status_code == 200

        parsed = yaml.safe_load(resp.content)
        tactic_ids = [t["id"] for t in parsed["tactics"].values()]
        assert tactic_ids == sorted([t1_id, t2_id])

    def test_export_matrix_sequences_keep_position_order(
        self,
        client: TestClient,
        db: Session,
        seed_collection_and_matrix: tuple[str, str],
    ) -> None:

        t1_id = client.post(
            f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload(name="Tactic A")
        ).json()["id"]
        t2_id = client.post(
            f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload(name="Tactic B")
        ).json()["id"]

        add_matrix_sequence(db, t1_id, position=2)
        add_matrix_sequence(db, t2_id, position=1)
        db.commit()

        resp = client.get(f"/versions/{ATLAS_DATA_VERSION}/data")
        assert resp.status_code == 200
        parsed = yaml.safe_load(resp.content)

        sequences = parsed["relationships"]["ATLAS-matrix"]["sequences"]
        assert [entry["target"] for entry in sequences] == [t2_id, t1_id]
        assert [entry["position"] for entry in sequences] == [1, 2]

    def test_export_subtechnique(
        self, client: TestClient, seed_collection_and_matrix: tuple[str, str]
    ) -> None:
        tactic_id = client.post(
            f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload()
        ).json()["id"]
        parent_id = client.post(
            f"/{ATLAS_DATA_VERSION}/techniques/",
            json=technique_payload(tactics=[{"tactic": tactic_id}]),
        ).json()["id"]
        client.post(
            f"/{ATLAS_DATA_VERSION}/techniques/",
            json=technique_payload(
                tactics=[{"tactic": tactic_id}],
                name="Sub",
                specializes={"technique": parent_id, "description": "specializes"},
            ),
        )

        resp = client.get(f"/versions/{ATLAS_DATA_VERSION}/data")
        assert resp.status_code == 200

        parsed = yaml.safe_load(resp.content)
        techniques = parsed["techniques"]
        assert len(techniques) == 2
        sub = next(t for t in techniques.values() if t["id"] != parent_id)
        assert "specializes" not in sub

        rels = parsed.get("relationships", {})
        assert sub["id"] in rels
        assert "specializes" in rels[sub["id"]]
        assert any(
            r["target"] == parent_id and r.get("description") == "specializes"
            for r in rels[sub["id"]]["specializes"]
        )

    def test_export_round_trip_pydantic(
        self,
        client: TestClient,
        db: Session,
        seed_collection_and_matrix: tuple[str, str],
    ) -> None:
        tactic_id = client.post(
            f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload()
        ).json()["id"]
        client.post(
            f"/{ATLAS_DATA_VERSION}/techniques/",
            json=technique_payload(tactics=[{"tactic": tactic_id}]),
        )
        client.post(
            f"/{ATLAS_DATA_VERSION}/mitigations/",
            json=mitigation_payload(mitigates=[{"technique": "AML.T0001"}]),
        )
        add_matrix_sequence(db, tactic_id)
        db.commit()

        resp = client.get(f"/versions/{ATLAS_DATA_VERSION}/data")
        assert resp.status_code == 200

        parsed = yaml.safe_load(resp.content)
        export = schemas.AtlasExport(**parsed)
        assert export.format_version == ATLAS_FORMAT_VERSION
        assert export.collection.version == ATLAS_DATA_VERSION
        assert len(export.techniques) == 1
        assert len(export.mitigations) == 1

    def test_export_parsing_ignores_unknown_fields(
        self,
        client: TestClient,
        db: Session,
        seed_collection_and_matrix: tuple[str, str],
    ) -> None:
        tactic_id = client.post(
            f"/{ATLAS_DATA_VERSION}/tactics/", json=tactic_payload()
        ).json()["id"]
        add_matrix_sequence(db, tactic_id)
        db.commit()

        resp = client.get(f"/versions/{ATLAS_DATA_VERSION}/data")
        assert resp.status_code == 200

        parsed = yaml.safe_load(resp.content)
        parsed["new-top-level-field"] = "future-compatible"
        parsed["collection"]["new-collection-field"] = "future-compatible"
        parsed["tactics"][tactic_id]["new-tactic-field"] = "future-compatible"
        parsed["relationships"]["ATLAS-matrix"]["sequences"][0][
            "new-relationship-field"
        ] = "future-compatible"

        export = schemas.AtlasExport(**parsed)
        assert export.collection.id == ATLAS_COLLECTION_ID
        assert tactic_id in export.tactics

    def test_export_round_trip_real_dataset(
        self, client: TestClient, loaded_real_dataset: tuple[str, schemas.AtlasExport]
    ) -> None:
        version, source_export = loaded_real_dataset

        resp = client.get(f"/versions/{version}/data")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/x-yaml"

        parsed = yaml.safe_load(resp.content)
        exported = schemas.AtlasExport(**parsed)
        assert exported.format_version == ATLAS_FORMAT_VERSION

        assert exported.collection.id == source_export.collection.id
        assert exported.collection.version == version
        assert exported.matrix.id == source_export.matrix.id

        assert len(exported.tactics) == len(source_export.tactics)
        assert len(exported.techniques) == len(source_export.techniques)
        assert len(exported.mitigations) == len(source_export.mitigations)
        assert len(exported.case_studies) == len(source_export.case_studies)

        assert set(exported.relationships.keys()) == set(
            source_export.relationships.keys()
        )

        matrix_relationships = exported.relationships.get("ATLAS-matrix")
        matrix_sequences = (
            matrix_relationships[AtlasRelationshipType.SEQUENCES]
            if matrix_relationships is not None
            and AtlasRelationshipType.SEQUENCES in matrix_relationships
            else []
        )
        positions = [
            entry.position for entry in matrix_sequences if entry.position is not None
        ]
        assert positions == sorted(positions)

        platform_order = {
            platform.value: index
            for index, platform in enumerate(TechniquePlatformType)
        }
        lifecycle_order = {
            phase.value: index
            for index, phase in enumerate(MitigationLifecyclePhasesType)
        }
        category_order = {
            category.value: index
            for index, category in enumerate(MitigationCategoryType)
        }

        for technique in exported.techniques.values():
            indices = [platform_order[value.value] for value in technique.platforms]
            assert indices == sorted(indices)

        for mitigation in exported.mitigations.values():
            lifecycle_indices = [
                lifecycle_order[value.value] for value in mitigation.lifecycle_phases
            ]
            category_indices = [
                category_order[value.value] for value in mitigation.categories
            ]
            assert lifecycle_indices == sorted(lifecycle_indices)
            assert category_indices == sorted(category_indices)
