"""Publication checks for authored maturity in the current release.

Set ATLAS_DATA_FILE to validate a different exported dataset.
"""

import os
from pathlib import Path

import pytest
import yaml

from atlas import schemas
from atlas.enums import ActivityPurpose, AtlasRelationshipType, CaseStudyType
from atlas.enums import TechniqueMaturity as Maturity


DATA_FILE = Path(
    os.environ.get(
        "ATLAS_DATA_FILE",
        str(Path(__file__).resolve().parents[1] / "dist/v6/ATLAS-latest.yaml"),
    )
)
EXPORT = schemas.AtlasExport.model_validate(yaml.safe_load(DATA_FILE.read_text()))
RANK = {Maturity.FEASIBLE: 0, Maturity.DEMONSTRATED: 1, Maturity.REALIZED: 2}
CASE_MINIMUM = {
    CaseStudyType.EXERCISE: Maturity.DEMONSTRATED,
    CaseStudyType.INCIDENT: Maturity.REALIZED,
}
ENTITY_MINIMUM = {
    ActivityPurpose.SECURITY_EVALUATION: Maturity.DEMONSTRATED,
    ActivityPurpose.ADVERSARIAL_OPERATION: Maturity.REALIZED,
    ActivityPurpose.UNINTENDED_CONSEQUENCE: Maturity.REALIZED,
}


def relationships(kind):
    return [
        pytest.param(rel, id=f"{rel.source}-{rel.target}-{rel.step_id or index}")
        for types in EXPORT.relationships.values()
        for index, rel in enumerate(types.get(kind, []))
    ]


def assert_minimum(technique_id, minimum, evidence):
    technique = EXPORT.techniques[technique_id]
    assert RANK[technique.maturity] >= RANK[minimum], (
        f"{technique.id} — {technique.name}: stored maturity "
        f"{technique.maturity.value} is below required {minimum.value}. "
        f"Evidence: {evidence}. Dataset: {DATA_FILE}"
    )


@pytest.mark.parametrize("rel", relationships(AtlasRelationshipType.EMPLOYS))
def test_case_study_maturity_minimum(rel):
    case_study = EXPORT.case_studies[rel.source]
    assert_minimum(
        rel.target,
        CASE_MINIMUM[case_study.type],
        f"{rel.source}, type {case_study.type.value}, relationship employs",
    )


@pytest.mark.parametrize("rel", relationships(AtlasRelationshipType.USES))
def test_entity_usage_maturity_minimum(rel):
    if rel.target in EXPORT.software:
        return
    assert rel.source in EXPORT.entities, f"Unknown entity: {rel.source}"
    assert_minimum(
        rel.target,
        ENTITY_MINIMUM[rel.activity_purpose],
        f"{rel.source}, purpose {rel.activity_purpose.value}, relationship uses",
    )


@pytest.mark.parametrize("rel", relationships(AtlasRelationshipType.SPECIALIZES))
def test_parent_maturity_minimum(rel):
    child = EXPORT.techniques[rel.source]
    assert_minimum(
        rel.target,
        child.maturity,
        f"sub-technique {rel.source}, relationship specializes",
    )
