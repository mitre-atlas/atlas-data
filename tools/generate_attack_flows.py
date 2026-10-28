# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyyaml>=6.0.3",
# ]
# ///

"""Generate Attack Flow 2.0 bundles from ATLAS case studies."""

import json
import uuid
from argparse import ArgumentParser
from collections.abc import Iterable
from datetime import UTC, date, datetime
from pathlib import Path

import yaml

ATTACK_FLOW_EXTENSION_ID = "extension-definition--fb9c968a-745b-4ade-9b25-c324172197f4"
ATTACK_FLOW_PUBLISHER_ID = "identity--d673f8cb-c168-42da-8ed4-0cb26725f86c"
ATLAS_IDENTITY_NAMESPACE = uuid.UUID("61746c61-732e-6d69-7472-652e6f72672e")
ID_NAMESPACE = uuid.UUID("7a5b4b3c-1f0c-4c3f-8a79-1e1a0f9f3d53")


def _stix_id(object_type: str, *parts: str) -> str:
    value = "\0".join(parts)
    return f"{object_type}--{uuid.uuid5(ID_NAMESPACE, value)}"


def _timestamp(value: date | datetime) -> str:
    if isinstance(value, str):
        value = date.fromisoformat(value)
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.combine(value, datetime.min.time())
    return (
        dt.replace(tzinfo=UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    )


def _extension() -> dict:
    return {
        "type": "extension-definition",
        "spec_version": "2.1",
        "id": ATTACK_FLOW_EXTENSION_ID,
        "created": "2022-08-02T19:34:35.143Z",
        "modified": "2022-08-02T19:34:35.143Z",
        "name": "Attack Flow",
        "description": "Extends STIX 2.1 with features to create Attack Flows.",
        "created_by_ref": ATTACK_FLOW_PUBLISHER_ID,
        "schema": "https://raw.githubusercontent.com/center-for-threat-informed-defense/attack-flow/main/stix/attack-flow-schema-2.0.0.json",
        "version": "2.0.0",
        "extension_types": ["new-sdo"],
        "external_references": [
            {
                "source_name": "Documentation",
                "description": "Documentation for Attack Flow",
                "url": "https://center-for-threat-informed-defense.github.io/attack-flow",
            },
            {
                "source_name": "GitHub",
                "description": "Source code repository for Attack Flow",
                "url": "https://github.com/center-for-threat-informed-defense/attack-flow",
            },
        ],
    }


def _identity() -> dict:
    identity_id = f"identity--{uuid.uuid5(ATLAS_IDENTITY_NAMESPACE, 'ATLAS-identity')}"
    return {
        "type": "identity",
        "spec_version": "2.1",
        "id": identity_id,
        "created": "2020-10-23T00:00:00.000Z",
        "modified": "2026-10-01T00:00:00.000Z",
        "name": "MITRE ATLAS",
        "identity_class": "organization",
    }


def _publisher_identity() -> dict:
    return {
        "type": "identity",
        "spec_version": "2.1",
        "id": ATTACK_FLOW_PUBLISHER_ID,
        "created": "2022-08-02T19:34:35.143Z",
        "modified": "2022-08-02T19:34:35.143Z",
        "name": "MITRE Center for Threat-Informed Defense",
        "identity_class": "organization",
    }


def _namespace(value):
    """Convert YAML's hyphenated keys into the attribute shape used below."""
    if isinstance(value, dict):
        return _AttributeMapping(
            {key.replace("-", "_"): _namespace(item) for key, item in value.items()}
        )
    if isinstance(value, list):
        return [_namespace(item) for item in value]
    return value


class _AttributeMapping(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


def _with_extension(obj: dict) -> dict:
    obj["extensions"] = {ATTACK_FLOW_EXTENSION_ID: {"extension_type": "new-sdo"}}
    return obj


def generate_attack_flow(
    case_study,
    employs: Iterable,
    techniques: dict | None = None,
    tactics: dict | None = None,
) -> dict:
    """Return one STIX 2.1 Attack Flow bundle for a case study.

    ``employs`` is expected to contain ATLAS employs relationship objects. The
    authored ``leads_to`` graph is preserved, including branches and repeated
    uses of the same technique.
    """
    relationships = list(employs)
    if not relationships:
        raise ValueError(f"{case_study.id}: attack chain is empty")
    by_step: dict[str, object] = {}
    for relationship in relationships:
        step_id = relationship.step_id
        if not step_id:
            raise ValueError(f"{case_study.id}: every attack-chain step needs step_id")
        if step_id in by_step:
            raise ValueError(f"{case_study.id}: duplicate step_id {step_id}")
        by_step[step_id] = relationship

    for relationship in relationships:
        for target_step in relationship.leads_to or []:
            if target_step not in by_step:
                raise ValueError(
                    f"{case_study.id}: step {relationship.step_id} leads to missing step "
                    f"{target_step}"
                )

    incoming = {
        target_step
        for relationship in relationships
        for target_step in relationship.leads_to or []
    }
    starts = [step_id for step_id in by_step if step_id not in incoming]
    if relationships and not starts:
        raise ValueError(f"{case_study.id}: attack chain has no starting step")

    created = _timestamp(case_study.created_date)
    modified = _timestamp(case_study.modified_date)
    action_ids = {
        step_id: _stix_id("attack-action", case_study.id, step_id)
        for step_id in by_step
    }
    technique_names = techniques or {}
    actions = []
    for step_id, relationship in by_step.items():
        if techniques is not None and relationship.target not in techniques:
            raise ValueError(
                f"{case_study.id}: unknown technique {relationship.target}"
            )
        if tactics is not None and relationship.tactic not in tactics:
            raise ValueError(f"{case_study.id}: unknown tactic {relationship.tactic}")
        technique = technique_names.get(relationship.target)
        action = {
            "type": "attack-action",
            "spec_version": "2.1",
            "id": action_ids[step_id],
            "created": created,
            "modified": modified,
            "name": getattr(technique, "name", relationship.target),
            "description": relationship.description or "",
            "technique_id": relationship.target,
            "tactic_id": relationship.tactic,
        }
        if relationship.leads_to:
            action["effect_refs"] = [
                action_ids[target] for target in relationship.leads_to
            ]
        _with_extension(action)
        actions.append(action)

    scope = "incident" if case_study.type == "Incident" else "emulation-plan"
    flow = {
        "type": "attack-flow",
        "spec_version": "2.1",
        "id": _stix_id("attack-flow", case_study.id),
        "created": created,
        "modified": modified,
        "name": case_study.name,
        "description": case_study.description,
        "scope": scope,
        "start_refs": [action_ids[step_id] for step_id in starts],
        "created_by_ref": _identity()["id"],
        "ttp_frameworks": {"ATL": True},
    }
    _with_extension(flow)

    bundle = {
        "type": "bundle",
        "id": _stix_id("bundle", case_study.id),
        "objects": [_extension(), flow, _publisher_identity(), _identity(), *actions],
    }
    return bundle


def generate_from_export(
    export, case_study_ids: list[str] | None = None
) -> dict[str, dict]:
    """Generate bundles for selected case studies in an ATLAS export."""
    ids = case_study_ids or list(export.case_studies)
    missing = [
        case_study_id
        for case_study_id in ids
        if case_study_id not in export.case_studies
    ]
    if missing:
        raise ValueError(f"Unknown case study ID(s): {', '.join(missing)}")

    output = {}
    for case_study_id in ids:
        case_study = export.case_studies[case_study_id]
        relationships = export.relationships.get(case_study_id, {}).get("employs", [])
        output[case_study_id] = generate_attack_flow(
            case_study,
            relationships,
            export.techniques,
            export.tactics,
        )
    return output


def main() -> None:
    parser = ArgumentParser(
        description="Generate Attack Flow JSON from ATLAS case studies."
    )
    parser.add_argument(
        "-i", "--input", type=Path, default=Path("dist/ATLAS-latest.yaml")
    )
    parser.add_argument("-o", "--output", type=Path, default=Path("dist/attack-flows"))
    parser.add_argument(
        "--case-study",
        action="append",
        dest="case_study_ids",
        metavar="ID",
        help="Case study ID to generate; repeat to select multiple (default: all).",
    )
    args = parser.parse_args()

    export = _namespace(yaml.safe_load(args.input.read_text()))
    bundles = generate_from_export(export, args.case_study_ids)
    args.output.mkdir(parents=True, exist_ok=True)
    for case_study_id, bundle in bundles.items():
        (args.output / f"{case_study_id}.json").write_text(
            json.dumps(bundle, indent=2) + "\n"
        )
    print(f"Generated {len(bundles)} Attack Flow file(s) in {args.output}")


if __name__ == "__main__":
    main()
