from __future__ import annotations

import json
import uuid
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path

import requests
import yaml
from stix2 import properties
from stix2.v21 import (
    AttackPattern,
    Bundle,
    Campaign,
    CourseOfAction,
    CustomObject,
    ExternalReference,
    Identity,
    IntrusionSet,
    KillChainPhase,
    Malware,
    Relationship,
    Tool,
)

from atlas import schemas
from atlas.enums import ActivityPurpose, AtlasRelationshipType, EntityType, SoftwareType

STIX_UUID_DOMAIN = uuid.UUID(b"atlas.mitre.org.".hex())


@CustomObject(
    "x-mitre-tactic",
    [
        ("name", properties.StringProperty()),
        ("description", properties.StringProperty()),
        ("external_references", properties.ListProperty(ExternalReference)),
        ("x_mitre_shortname", properties.StringProperty()),
        ("x_mitre_domains", properties.ListProperty(properties.StringProperty())),
    ],
)
class AttackTactic:
    def __init__(self, **kwargs):
        pass


@CustomObject(
    "x-mitre-matrix",
    [
        ("name", properties.StringProperty()),
        ("description", properties.StringProperty()),
        ("external_references", properties.ListProperty(ExternalReference)),
        (
            "tactic_refs",
            properties.ListProperty(
                properties.ReferenceProperty(valid_types="x-mitre-tactic")
            ),
        ),
    ],
)
class AttackMatrix:
    def __init__(self, **kwargs):
        pass


@CustomObject(
    "x-mitre-collection",
    [
        ("type", properties.StringProperty()),
        ("id", properties.IDProperty(type="x-mitre-collection")),
        ("name", properties.StringProperty()),
        ("description", properties.StringProperty()),
        ("created", properties.TimestampProperty()),
        ("modified", properties.TimestampProperty()),
        ("x_mitre_version", properties.StringProperty()),
        ("spec_version", properties.StringProperty()),
        ("x_mitre_attack_spec_version", properties.StringProperty()),
        ("created_by_ref", properties.ReferenceProperty(valid_types="identity")),
        (
            "object_marking_refs",
            properties.ListProperty(properties.IDProperty(type="x-mitre-collection")),
        ),
        ("x_mitre_contents", properties.ListProperty(properties.DictionaryProperty())),
    ],
)
class AttackCollection:
    def __init__(self, **kwargs):
        pass


def _ts(value) -> str:
    return f"{value.isoformat()}T00:00:00.000Z"


def _slug(value: str) -> str:
    return value.lower().replace(" ", "-")


def _atlas_ref(obj_id: str, atlas_url: str, source_name: str, route: str):
    return [
        ExternalReference(
            source_name=source_name,
            url=f"{atlas_url}/{route}/{obj_id}",
            external_id=obj_id,
        )
    ]


def _attack_ref(obj) -> ExternalReference | None:
    attack_ref = getattr(obj, "attack_reference", None)
    if not attack_ref:
        return None
    return ExternalReference(
        source_name="mitre-attack",
        external_id=attack_ref.id,
        url=str(attack_ref.url),
    )


def _relationship_id(source_ref: str, relationship_type: str, target_ref: str) -> str:
    relationship_uuid = uuid.uuid5(
        STIX_UUID_DOMAIN,
        f"{source_ref}\0{relationship_type}\0{target_ref}",
    )
    return f"relationship--{relationship_uuid}"


def get_latest_attack_stix_json(domain: str = "enterprise-attack") -> dict:
    resp = requests.get(
        f"https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/{domain}/{domain}.json",
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def load_attack_stix_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


class AtlasToStix:
    def __init__(
        self,
        export: schemas.AtlasExport,
        source_name: str,
        atlas_url: str,
        identity_name: str,
        include_case_studies: bool,
        maturity_threshold: str,
        existing_stix_json: dict | None = None,
    ):
        self.export = export
        self.source_name = source_name
        self.atlas_url = atlas_url.rstrip("/")
        self.identity_name = identity_name
        self.include_case_studies = include_case_studies
        self.maturity_threshold = maturity_threshold
        self.existing_stix_json = existing_stix_json

        self.tactic_stix_by_id: dict[str, AttackTactic] = {}
        self.tactic_ref_by_id: dict[str, str] = {}
        self.technique_stix_by_id: dict[str, AttackPattern] = {}
        self.mitigation_stix_by_id: dict[str, CourseOfAction] = {}
        self.case_study_stix_by_id: dict[str, Campaign] = {}
        self.entity_stix_by_id: dict[str, IntrusionSet | Identity] = {}
        self.software_stix_by_id: dict[str, Malware | Tool] = {}

        self.achieves_by_source: dict[str, list[schemas.AtlasRelationship]] = (
            defaultdict(list)
        )
        self.specializes_edges: list[schemas.AtlasRelationship] = []
        self.mitigates_edges: list[schemas.AtlasRelationship] = []
        self.sequence_edges: list[schemas.AtlasRelationship] = []
        self.employs_edges: list[schemas.AtlasRelationship] = []
        self.attributed_to_edges: list[schemas.AtlasRelationship] = []
        self.uses_edges: list[schemas.AtlasRelationship] = []
        self.implements_edges: list[schemas.AtlasRelationship] = []

        self._collect_relationships()
        self.allowed_technique_ids = self._allowed_technique_ids()
        self.allowed_case_study_ids = self._allowed_case_study_ids()

    def _allowed_technique_ids(self) -> set[str]:
        if self.maturity_threshold == "feasible":
            return set(self.export.techniques.keys())

        if self.maturity_threshold == "demonstrated":
            return {
                tid
                for tid, t in self.export.techniques.items()
                if t.maturity.value in ("Demonstrated", "Realized")
            }

        # realized
        return {
            tid
            for tid, t in self.export.techniques.items()
            if t.maturity.value == "Realized"
        }

    def _allowed_case_study_ids(self) -> set[str]:
        if self.maturity_threshold != "realized":
            return set(self.export.case_studies.keys())

        return {
            cs_id
            for cs_id, cs in self.export.case_studies.items()
            if cs.type.value == "Incident"
        }

    def _collect_relationships(self) -> None:
        for _, rels_by_type in self.export.relationships.items():
            for rel_type, rels in rels_by_type.items():
                if rel_type == AtlasRelationshipType.ACHIEVES:
                    for rel in rels:
                        self.achieves_by_source[rel.source].append(rel)
                elif rel_type == AtlasRelationshipType.SPECIALIZES:
                    self.specializes_edges.extend(rels)
                elif rel_type == AtlasRelationshipType.MITIGATES:
                    self.mitigates_edges.extend(rels)
                elif rel_type == AtlasRelationshipType.SEQUENCES:
                    self.sequence_edges.extend(rels)
                elif rel_type == AtlasRelationshipType.EMPLOYS:
                    self.employs_edges.extend(rels)
                elif rel_type == AtlasRelationshipType.ATTRIBUTED_TO:
                    self.attributed_to_edges.extend(rels)
                elif rel_type == AtlasRelationshipType.USES:
                    self.uses_edges.extend(rels)
                elif rel_type == AtlasRelationshipType.IMPLEMENTS:
                    self.implements_edges.extend(rels)

        for source, rels in self.achieves_by_source.items():
            self.achieves_by_source[source] = sorted(rels, key=lambda rel: rel.target)
        self.specializes_edges.sort(key=lambda rel: (rel.source, rel.target))
        self.mitigates_edges.sort(key=lambda rel: (rel.source, rel.target))
        self.sequence_edges.sort(
            key=lambda rel: (
                rel.position if rel.position is not None else 2**31 - 1,
                rel.target,
            )
        )
        self.employs_edges.sort(
            key=lambda rel: (rel.source, rel.step_id or "", rel.target)
        )
        self.attributed_to_edges.sort(key=lambda rel: (rel.source, rel.target))
        self.uses_edges.sort(key=lambda rel: (rel.source, rel.target))
        self.implements_edges.sort(key=lambda rel: (rel.source, rel.target))

    def _append_relationship(
        self,
        relationships: list[Relationship],
        seen_triples: set[tuple[str, str, str]],
        source_ref: str,
        relationship_type: str,
        target_ref: str,
        description: str | None,
        created: str,
        modified: str,
    ) -> None:
        triple = (source_ref, relationship_type, target_ref)
        if triple in seen_triples:
            return
        seen_triples.add(triple)
        relationships.append(
            Relationship(
                id=_relationship_id(*triple),
                source_ref=source_ref,
                relationship_type=relationship_type,
                target_ref=target_ref,
                description=description,
                created=created,
                modified=modified,
                allow_custom=relationship_type.startswith("x-"),
            )
        )

    def _entity_use_meets_threshold(self, rel: schemas.AtlasRelationship) -> bool:
        if rel.activity_purpose in {
            ActivityPurpose.ADVERSARIAL_OPERATION,
            ActivityPurpose.UNINTENDED_CONSEQUENCE,
        }:
            return True
        return self.maturity_threshold != "realized"

    def _kill_chain_for_technique(self, technique_id: str) -> list[KillChainPhase]:
        phases: list[KillChainPhase] = []
        for rel in self.achieves_by_source.get(technique_id, []):
            tactic = self.export.tactics.get(rel.target)
            if tactic is None:
                continue
            phases.append(
                KillChainPhase(
                    kill_chain_name=self.source_name,
                    phase_name=_slug(tactic.name),
                )
            )
        return phases

    def build(self) -> dict:
        stix_relationships: list[Relationship] = []
        seen_relationship_triples: set[tuple[str, str, str]] = set()

        for tactic_id in sorted(self.export.tactics):
            t = self.export.tactics[tactic_id]
            refs = _atlas_ref(t.id, self.atlas_url, self.source_name, "tactics")
            attack_ref = _attack_ref(t)
            if attack_ref is not None:
                refs.append(attack_ref)

            self.tactic_stix_by_id[t.id] = AttackTactic(
                id=f"x-mitre-tactic--{t.uuid}",
                name=t.name,
                description=t.description,
                external_references=refs,
                x_mitre_shortname=_slug(t.name),
                x_mitre_domains=["ATLAS"],
                created=_ts(t.created_date),
                modified=_ts(t.modified_date),
            )
            self.tactic_ref_by_id[t.id] = f"x-mitre-tactic--{t.uuid}"

        specializes_children = {rel.source for rel in self.specializes_edges}

        for technique_id in sorted(self.export.techniques):
            if technique_id not in self.allowed_technique_ids:
                continue
            t = self.export.techniques[technique_id]
            refs = _atlas_ref(t.id, self.atlas_url, self.source_name, "techniques")
            attack_ref = _attack_ref(t)
            if attack_ref is not None:
                refs.append(attack_ref)

            kwargs = {
                "id": f"attack-pattern--{t.uuid}",
                "name": t.name,
                "description": t.description,
                "kill_chain_phases": self._kill_chain_for_technique(t.id),
                "external_references": refs,
                "allow_custom": True,
                "x_mitre_platforms": [platform.value for platform in t.platforms],
                "x_mitre_domains": ["ATLAS"],
                "created": _ts(t.created_date),
                "modified": _ts(t.modified_date),
            }
            if t.id in specializes_children:
                kwargs["x_mitre_is_subtechnique"] = True

            self.technique_stix_by_id[t.id] = AttackPattern(**kwargs)

        for mitigation_id in sorted(self.export.mitigations):
            m = self.export.mitigations[mitigation_id]
            refs = _atlas_ref(m.id, self.atlas_url, self.source_name, "mitigations")
            attack_ref = _attack_ref(m)
            if attack_ref is not None:
                refs.append(attack_ref)

            self.mitigation_stix_by_id[m.id] = CourseOfAction(
                id=f"course-of-action--{m.uuid}",
                name=m.name,
                description=m.description,
                external_references=refs,
                allow_custom=True,
                x_mitre_domains=["ATLAS"],
                created=_ts(m.created_date),
                modified=_ts(m.modified_date),
            )

        if self.include_case_studies:
            for case_study_id in sorted(self.export.case_studies):
                if case_study_id not in self.allowed_case_study_ids:
                    continue
                cs = self.export.case_studies[case_study_id]
                refs = _atlas_ref(cs.id, self.atlas_url, self.source_name, "studies")
                self.case_study_stix_by_id[cs.id] = Campaign(
                    id=f"campaign--{cs.uuid}",
                    name=cs.name,
                    description=cs.description,
                    external_references=refs,
                    created=_ts(cs.created_date),
                    modified=_ts(cs.modified_date),
                )

        for entity_id in sorted(self.export.entities):
            entity = self.export.entities[entity_id]
            refs = _atlas_ref(entity.id, self.atlas_url, self.source_name, "entities")
            attack_ref = _attack_ref(entity)
            if attack_ref is not None:
                refs.append(attack_ref)

            associated_group_refs = []
            for associated_entity in entity.associated_entities:
                if associated_entity.description:
                    associated_group_refs.append(
                        {
                            "source_name": associated_entity.name,
                            "description": associated_entity.description,
                        }
                    )
            refs.extend(associated_group_refs)

            if entity.entity_type == EntityType.ACTIVITY_CLUSTER:
                aliases = []
                seen_names = {entity.name.casefold()}
                for associated_entity in entity.associated_entities:
                    alias = associated_entity.name
                    normalized_name = alias.casefold()
                    if normalized_name in seen_names:
                        continue
                    aliases.append(alias)
                    seen_names.add(normalized_name)
                kwargs = {
                    "id": f"intrusion-set--{entity.uuid}",
                    "name": entity.name,
                    "description": entity.description,
                    "external_references": refs,
                    "created": _ts(entity.created_date),
                    "modified": _ts(entity.modified_date),
                }
                if aliases:
                    kwargs["aliases"] = aliases
                self.entity_stix_by_id[entity.id] = IntrusionSet(**kwargs)
            else:
                identity_class = {
                    EntityType.ORGANIZATION: "organization",
                    EntityType.TEAM: "group",
                    EntityType.INDIVIDUAL: "individual",
                }[entity.entity_type]
                self.entity_stix_by_id[entity.id] = Identity(
                    id=f"identity--{entity.uuid}",
                    name=entity.name,
                    description=entity.description,
                    identity_class=identity_class,
                    external_references=refs,
                    created=_ts(entity.created_date),
                    modified=_ts(entity.modified_date),
                )

        for software_id in sorted(self.export.software):
            software = self.export.software[software_id]
            refs = _atlas_ref(software.id, self.atlas_url, self.source_name, "software")
            attack_ref = _attack_ref(software)
            if attack_ref is not None:
                refs.append(attack_ref)
            kwargs = {
                "id": (
                    f"malware--{software.uuid}"
                    if software.software_type == SoftwareType.MALWARE
                    else f"tool--{software.uuid}"
                ),
                "name": software.name,
                "description": software.description,
                "external_references": refs,
                "created": _ts(software.created_date),
                "modified": _ts(software.modified_date),
            }
            if software.software_type == SoftwareType.MALWARE:
                if software.aliases:
                    kwargs["aliases"] = software.aliases
                self.software_stix_by_id[software.id] = Malware(
                    **kwargs, is_family=True
                )
            else:
                self.software_stix_by_id[software.id] = Tool(**kwargs)

        for rel in self.specializes_edges:
            if (
                rel.source not in self.allowed_technique_ids
                or rel.target not in self.allowed_technique_ids
            ):
                continue
            source = self.technique_stix_by_id.get(rel.source)
            target = self.technique_stix_by_id.get(rel.target)
            if source is None or target is None:
                continue
            source_technique = self.export.techniques.get(rel.source)
            rel_created = (
                _ts(source_technique.created_date)
                if source_technique is not None
                else _ts(self.export.collection.created_date)
            )
            rel_modified = (
                _ts(source_technique.modified_date)
                if source_technique is not None
                else _ts(self.export.collection.modified_date)
            )
            self._append_relationship(
                stix_relationships,
                seen_relationship_triples,
                source.id,
                "subtechnique-of",
                target.id,
                rel.description,
                rel_created,
                rel_modified,
            )

        for rel in self.mitigates_edges:
            if rel.target not in self.allowed_technique_ids:
                continue
            source = self.mitigation_stix_by_id.get(rel.source)
            target = self.technique_stix_by_id.get(rel.target)
            if source is None or target is None:
                continue
            source_mitigation = self.export.mitigations.get(rel.source)
            rel_created = (
                _ts(source_mitigation.created_date)
                if source_mitigation is not None
                else _ts(self.export.collection.created_date)
            )
            rel_modified = (
                _ts(source_mitigation.modified_date)
                if source_mitigation is not None
                else _ts(self.export.collection.modified_date)
            )
            self._append_relationship(
                stix_relationships,
                seen_relationship_triples,
                source.id,
                "mitigates",
                target.id,
                rel.description,
                rel_created,
                rel_modified,
            )

        if self.include_case_studies:
            for rel in self.employs_edges:
                if (
                    rel.source not in self.allowed_case_study_ids
                    or rel.target not in self.allowed_technique_ids
                ):
                    continue
                source = self.case_study_stix_by_id.get(rel.source)
                target = self.technique_stix_by_id.get(rel.target)
                if source is None or target is None:
                    continue

                source_case_study = self.export.case_studies.get(rel.source)
                rel_created = (
                    _ts(source_case_study.created_date)
                    if source_case_study is not None
                    else _ts(self.export.collection.created_date)
                )
                rel_modified = (
                    _ts(source_case_study.modified_date)
                    if source_case_study is not None
                    else _ts(self.export.collection.modified_date)
                )
                self._append_relationship(
                    stix_relationships,
                    seen_relationship_triples,
                    source.id,
                    "uses",
                    target.id,
                    rel.description,
                    rel_created,
                    rel_modified,
                )

            for rel in self.attributed_to_edges:
                source = self.case_study_stix_by_id.get(rel.source)
                target = self.entity_stix_by_id.get(rel.target)
                if source is None or target is None:
                    continue
                source_case_study = self.export.case_studies[rel.source]
                self._append_relationship(
                    stix_relationships,
                    seen_relationship_triples,
                    source.id,
                    "attributed-to",
                    target.id,
                    rel.description,
                    _ts(source_case_study.created_date),
                    _ts(source_case_study.modified_date),
                )

        for rel in self.uses_edges:
            source_object = self.export.entities.get(rel.source)
            source = self.entity_stix_by_id.get(rel.source)
            if rel.source in self.export.case_studies:
                source_object = self.export.case_studies[rel.source]
                source = self.case_study_stix_by_id.get(rel.source)
            if source is None or source_object is None:
                continue

            target = self.software_stix_by_id.get(rel.target)
            if target is None and rel.target in self.allowed_technique_ids:
                target = self.technique_stix_by_id.get(rel.target)
            if target is None:
                continue

            if (
                rel.target in self.export.techniques
                and not self._entity_use_meets_threshold(rel)
            ):
                continue
            self._append_relationship(
                stix_relationships,
                seen_relationship_triples,
                source.id,
                "uses",
                target.id,
                rel.description,
                _ts(source_object.created_date),
                _ts(source_object.modified_date),
            )

        for rel in self.implements_edges:
            if rel.target not in self.allowed_technique_ids:
                continue
            source = self.software_stix_by_id.get(rel.source)
            target = self.technique_stix_by_id.get(rel.target)
            source_software = self.export.software.get(rel.source)
            if source is None or target is None or source_software is None:
                continue
            self._append_relationship(
                stix_relationships,
                seen_relationship_triples,
                source.id,
                "uses",
                target.id,
                rel.description,
                _ts(source_software.created_date),
                _ts(source_software.modified_date),
            )

        sequence_edges = [
            rel for rel in self.sequence_edges if rel.source == self.export.matrix.id
        ]
        if sequence_edges:
            tactic_refs = [
                self.tactic_ref_by_id[rel.target]
                for rel in sequence_edges
                if rel.target in self.tactic_ref_by_id
            ]
        else:
            tactic_refs = [
                self.tactic_ref_by_id[tactic_id]
                for tactic_id in sorted(self.export.tactics)
                if tactic_id in self.tactic_ref_by_id
            ]

        matrix_refs = _atlas_ref(
            self.export.matrix.id,
            self.atlas_url,
            self.source_name,
            "matrix",
        )
        stix_matrix_obj = AttackMatrix(
            id=f"x-mitre-matrix--{self.export.matrix.uuid}",
            name=self.export.matrix.name,
            description=self.export.matrix.description,
            external_references=matrix_refs,
            tactic_refs=tactic_refs,
            allow_custom=True,
            created=_ts(self.export.matrix.created_date),
            modified=_ts(self.export.matrix.modified_date),
        )

        identity_uuid = uuid.uuid5(STIX_UUID_DOMAIN, "ATLAS-identity")
        identity = Identity(
            id=f"identity--{identity_uuid}",
            name=self.identity_name,
            description=self.atlas_url,
            created=_ts(self.export.collection.created_date),
            modified=_ts(self.export.collection.modified_date),
        )

        stix_data_objects = (
            list(self.tactic_stix_by_id.values())
            + list(self.technique_stix_by_id.values())
            + list(self.mitigation_stix_by_id.values())
            + list(self.case_study_stix_by_id.values())
            + list(self.entity_stix_by_id.values())
            + list(self.software_stix_by_id.values())
            + stix_relationships
            + [stix_matrix_obj]
        )

        stix_collection_obj = AttackCollection(
            id=f"x-mitre-collection--{self.export.collection.uuid}",
            type="x-mitre-collection",
            name=self.export.collection.name,
            description=self.export.collection.description,
            created=_ts(self.export.collection.created_date),
            modified=_ts(self.export.collection.modified_date),
            spec_version="2.1",
            x_mitre_version=self.export.collection.version,
            x_mitre_attack_spec_version="2.1.0",
            created_by_ref=identity.id,
            object_marking_refs=[],
            x_mitre_contents=[
                {
                    "object_ref": obj.id,
                    "object_modified": obj.modified,
                }
                for obj in stix_data_objects
                if hasattr(obj, "id") and hasattr(obj, "modified")
            ],
        )

        bundle_uuid = uuid.uuid5(STIX_UUID_DOMAIN, "ATLAS-bundle")
        bundle = Bundle(
            id=f"bundle--{bundle_uuid}",
            objects=stix_data_objects + [identity, stix_collection_obj],
            allow_custom=True,
        )
        stix_json = json.loads(bundle.serialize())

        if self.existing_stix_json:
            existing_objs = []
            merged_relationship_triples: set[tuple[str, str, str]] = set()
            for obj in self.existing_stix_json.get("objects", []):
                if (
                    obj.get("type") == "x-mitre-matrix"
                    and obj.get("name") == "Enterprise ATT&CK"
                ):
                    continue
                if (
                    "x_mitre_domains" in obj
                    and "enterprise-attack" in obj["x_mitre_domains"]
                ):
                    if "atlas-atlas" not in obj["x_mitre_domains"]:
                        obj["x_mitre_domains"].append("atlas-atlas")
                if obj.get("type") == "relationship":
                    triple = (
                        obj.get("source_ref"),
                        obj.get("relationship_type"),
                        obj.get("target_ref"),
                    )
                    if triple in merged_relationship_triples:
                        continue
                    merged_relationship_triples.add(triple)
                existing_objs.append(obj)
            for obj in stix_json["objects"]:
                if obj.get("type") == "relationship":
                    triple = (
                        obj.get("source_ref"),
                        obj.get("relationship_type"),
                        obj.get("target_ref"),
                    )
                    if triple in merged_relationship_triples:
                        continue
                    merged_relationship_triples.add(triple)
                existing_objs.append(obj)
            self.existing_stix_json["objects"] = existing_objs
            return self.existing_stix_json

        return stix_json


def main() -> None:
    parser = ArgumentParser(
        description="Create STIX JSON from ATLAS-latest.yaml export format."
    )
    parser.add_argument(
        "-i",
        type=Path,
        dest="atlas_data_filepath",
        default="./dist/ATLAS-latest.yaml",
        help="Path to ATLAS YAML file",
    )
    parser.add_argument(
        "-o",
        type=str,
        dest="output_filepath",
        default="dist/stix-atlas.json",
        help="Output filepath for STIX JSON",
    )
    parser.add_argument(
        "--url",
        type=str,
        dest="atlas_url",
        default="https://atlas.mitre.org",
        help="URL to ATLAS website for external references",
    )
    parser.add_argument(
        "--source_name",
        type=str,
        dest="source_name",
        default="mitre-atlas",
        help="Lowercase, hyphenated source identifier",
    )
    parser.add_argument(
        "--identity_name",
        type=str,
        dest="identity_name",
        default="MITRE ATLAS",
        help="Name of the creator identity",
    )
    parser.add_argument(
        "--include-attack",
        dest="include_attack",
        default=False,
        action="store_true",
        help="Include latest ATT&CK Enterprise STIX data",
    )
    parser.add_argument(
        "--attack-input",
        type=Path,
        help="Use a local ATT&CK STIX JSON snapshot with --include-attack",
    )
    parser.add_argument(
        "--include-case-studies",
        dest="include_case_studies",
        default=False,
        action="store_true",
        help="Include case studies as campaigns and campaign-to-technique uses relationships",
    )
    parser.add_argument(
        "--maturity-threshold",
        choices=["feasible", "demonstrated", "realized"],
        default="feasible",
        help="Filter techniques/campaigns by maturity threshold",
    )
    args = parser.parse_args()

    output_filepath = Path(args.output_filepath)
    output_filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(args.atlas_data_filepath) as f:
        payload = yaml.safe_load(f)
    export = schemas.AtlasExport(**payload)

    attack_stix_json = None
    if args.include_attack:
        attack_stix_json = (
            load_attack_stix_json(args.attack_input)
            if args.attack_input is not None
            else get_latest_attack_stix_json()
        )

    converter = AtlasToStix(
        export=export,
        source_name=args.source_name,
        atlas_url=args.atlas_url,
        identity_name=args.identity_name,
        include_case_studies=args.include_case_studies,
        maturity_threshold=args.maturity_threshold,
        existing_stix_json=attack_stix_json,
    )
    stix_json = converter.build()

    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(stix_json, f)

    print(f"Wrote STIX JSON to {output_filepath}")


if __name__ == "__main__":
    main()
