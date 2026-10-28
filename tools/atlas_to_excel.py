from __future__ import annotations

import re
from argparse import ArgumentParser
from collections import defaultdict
from datetime import date
from pathlib import Path

import pandas as pd
import yaml

from atlas import schemas
from atlas.constants import ATLAS_MATRIX_ID
from atlas.enums import AtlasRelationshipType, DateGranularity


def _format_date(dt: date) -> str:
    return dt.strftime("%d %B %Y")


def _format_case_study_date(dt: date, granularity: DateGranularity) -> str:
    if granularity == DateGranularity.YEAR:
        return dt.strftime("%Y")
    if granularity == DateGranularity.MONTH:
        return dt.strftime("%Y-%m")
    return dt.strftime("%Y-%m-%d")


def _format_references(references: list[schemas.Reference]) -> str:
    return "; ".join(
        f"{ref.id}: {ref.title} ({ref.url})"
        for ref in sorted(references, key=lambda x: x.id)
    )


def _stix_id(stix_type: str, obj_uuid: str) -> str:
    return f"{stix_type}--{obj_uuid}"


def _atlas_object_url(atlas_url: str, obj_id: str) -> str:
    if obj_id.startswith("AML.TA"):
        route = "tactics"
    elif obj_id.startswith("AML.T"):
        route = "techniques"
    elif obj_id.startswith("AML.M"):
        route = "mitigations"
    elif obj_id.startswith("AML.CS"):
        route = "case-studies"
    elif obj_id.startswith("AML.E"):
        route = "entities"
    elif obj_id.startswith("AML.S"):
        route = "software"
    else:
        route = "objects"
    return f"{atlas_url.rstrip('/')}/{route}/{obj_id}"


def _load_data(path: Path) -> schemas.AtlasExport:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    data.setdefault("format-version", "1.0.0")
    return schemas.AtlasExport.model_validate(data)


def _build_tactics_df(atlas_data: schemas.AtlasExport, atlas_url: str) -> pd.DataFrame:
    rows = []
    for tactic in sorted(atlas_data.tactics.values(), key=lambda x: x.id):
        rows.append(
            {
                "ID": tactic.id,
                "STIX ID": _stix_id("x-mitre-tactic", tactic.uuid),
                "name": tactic.name,
                "description": tactic.description,
                "url": _atlas_object_url(atlas_url, tactic.id),
                "created": _format_date(tactic.created_date),
                "last modified": _format_date(tactic.modified_date),
            }
        )
    return pd.DataFrame(rows)


def _build_techniques_df(
    atlas_data: schemas.AtlasExport, atlas_url: str
) -> pd.DataFrame:
    tactic_name_by_id = {t.id: t.name for t in atlas_data.tactics.values()}
    tactic_ids_by_technique: dict[str, set[str]] = defaultdict(set)
    for source, rels_by_type in atlas_data.relationships.items():
        for rel in rels_by_type.get(AtlasRelationshipType.ACHIEVES, []):
            tactic_ids_by_technique[source].add(rel.target)

    rows = []
    for technique in sorted(atlas_data.techniques.values(), key=lambda x: x.id):
        rows.append(
            {
                "ID": technique.id,
                "STIX ID": _stix_id("attack-pattern", technique.uuid),
                "name": technique.name,
                "description": technique.description,
                "url": _atlas_object_url(atlas_url, technique.id),
                "created": _format_date(technique.created_date),
                "last modified": _format_date(technique.modified_date),
                "tactics": ", ".join(
                    sorted(
                        tactic_name_by_id[tactic_id]
                        for tactic_id in tactic_ids_by_technique.get(
                            technique.id, set()
                        )
                        if tactic_id in tactic_name_by_id
                    )
                ),
                "platforms": ", ".join(
                    platform.value for platform in technique.platforms
                ),
            }
        )
    return pd.DataFrame(rows)


def _build_mitigation_dataframes(
    atlas_data: schemas.AtlasExport,
    atlas_url: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    relationships = atlas_data.relationships
    mitigates_rows = []
    mitigates_by_mitigation: dict[str, list[str]] = defaultdict(list)

    for source, rels_by_type in relationships.items():
        for rel in rels_by_type.get(AtlasRelationshipType.MITIGATES, []):
            if (
                source not in atlas_data.mitigations
                or rel.target not in atlas_data.techniques
            ):
                continue
            mitigation = atlas_data.mitigations[source]
            technique = atlas_data.techniques[rel.target]
            mitigates_by_mitigation[source].append(rel.description or "")
            mitigates_rows.append(
                {
                    "source ID": mitigation.id,
                    "source name": mitigation.name,
                    "source ref": _stix_id("course-of-action", mitigation.uuid),
                    "source type": "mitigation",
                    "mapping type": "mitigates",
                    "target ID": technique.id,
                    "target name": technique.name,
                    "target ref": _stix_id("attack-pattern", technique.uuid),
                    "target type": "technique",
                    "mapping description": rel.description,
                    "STIX ID": _stix_id(
                        "relationship",
                        f"{mitigation.uuid}-{technique.uuid}-mitigates",
                    ),
                    "created": _format_date(mitigation.created_date),
                    "last modified": _format_date(mitigation.modified_date),
                }
            )

    mitigation_rows = []
    for mitigation in sorted(atlas_data.mitigations.values(), key=lambda x: x.id):
        descriptions = " ".join(
            filter(None, mitigates_by_mitigation.get(mitigation.id, []))
        )
        citations = sorted(set(re.findall(r"\(Citation: (.*?)\)", descriptions)))
        mitigation_rows.append(
            {
                "ID": mitigation.id,
                "STIX ID": _stix_id("course-of-action", mitigation.uuid),
                "name": mitigation.name,
                "description": mitigation.description,
                "url": _atlas_object_url(atlas_url, mitigation.id),
                "created": _format_date(mitigation.created_date),
                "last modified": _format_date(mitigation.modified_date),
                "relationship citations": ",".join(
                    f"(Citation: {citation})" for citation in citations
                ),
            }
        )

    mitigations_df = pd.DataFrame(mitigation_rows)
    techniques_addressed_df = pd.DataFrame(mitigates_rows)
    if not techniques_addressed_df.empty:
        techniques_addressed_df = techniques_addressed_df.sort_values(
            ["source ID", "target ID"]
        )
    return mitigations_df, techniques_addressed_df


def _build_case_study_dataframes(
    atlas_data: schemas.AtlasExport,
    atlas_url: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    case_study_rows = []
    techniques_used_rows = []
    entities_attributed_rows = []
    entities_reporting_rows = []
    software_used_rows = []

    tactic_name_by_id = {
        tactic.id: tactic.name for tactic in atlas_data.tactics.values()
    }

    for case_study in sorted(atlas_data.case_studies.values(), key=lambda x: x.id):
        case_study_rows.append(
            {
                "ID": case_study.id,
                "STIX ID": _stix_id("campaign", case_study.uuid),
                "name": case_study.name,
                "description": case_study.description,
                "url": _atlas_object_url(atlas_url, case_study.id),
                "created": _format_date(case_study.created_date),
                "last modified": _format_date(case_study.modified_date),
                "type": case_study.type.value,
                "verbatim scalar actor attribution": case_study.actor,
                "target": case_study.target,
                "reporter": case_study.reporter or "",
                "start date": _format_case_study_date(
                    case_study.start_date, case_study.start_date_granularity
                ),
                "start date granularity": case_study.start_date_granularity.value,
                "end date": (
                    _format_case_study_date(
                        case_study.end_date, case_study.end_date_granularity
                    )
                    if case_study.end_date is not None
                    else ""
                ),
                "end date granularity": (
                    case_study.end_date_granularity.value
                    if case_study.end_date_granularity is not None
                    else ""
                ),
                "references": _format_references(case_study.references),
            }
        )

        employs = atlas_data.relationships.get(case_study.id, {}).get(
            AtlasRelationshipType.EMPLOYS, []
        )
        for rel in sorted(employs, key=lambda x: (x.position or 0, x.step_id or "")):
            technique = atlas_data.techniques.get(rel.target)
            techniques_used_rows.append(
                {
                    "case study ID": case_study.id,
                    "case study name": case_study.name,
                    "step ID": rel.step_id or "",
                    "source type": "case-study",
                    "source ID": case_study.id,
                    "source name": case_study.name,
                    "target technique ID": rel.target,
                    "target technique name": technique.name if technique else "",
                    "tactic ID": rel.tactic or "",
                    "tactic name": tactic_name_by_id.get(rel.tactic, "")
                    if rel.tactic
                    else "",
                    "description": rel.description or "",
                    "leads to": ", ".join(rel.leads_to or []),
                }
            )

        attributed_to = atlas_data.relationships.get(case_study.id, {}).get(
            AtlasRelationshipType.ATTRIBUTED_TO, []
        )
        for rel in sorted(attributed_to, key=lambda x: x.target):
            entity = atlas_data.entities.get(rel.target)
            entities_attributed_rows.append(
                {
                    "case study ID": case_study.id,
                    "case study name": case_study.name,
                    "source type": "case-study",
                    "source ID": case_study.id,
                    "source name": case_study.name,
                    "target entity ID": rel.target,
                    "target entity name": entity.name if entity else "",
                    "target entity type": entity.entity_type.value if entity else "",
                    "activity purpose": rel.activity_purpose.value
                    if rel.activity_purpose
                    else "",
                    "description": rel.description or "",
                }
            )

        reported_by = atlas_data.relationships.get(case_study.id, {}).get(
            AtlasRelationshipType.REPORTED_BY, []
        )
        for rel in sorted(reported_by, key=lambda x: x.target):
            entity = atlas_data.entities[rel.target]
            entities_reporting_rows.append(
                {
                    "case study ID": case_study.id,
                    "case study name": case_study.name,
                    "source type": "case-study",
                    "source ID": case_study.id,
                    "source name": case_study.name,
                    "target entity ID": entity.id,
                    "target entity name": entity.name,
                    "target entity type": entity.entity_type.value,
                    "description": rel.description or "",
                }
            )

        uses = atlas_data.relationships.get(case_study.id, {}).get(
            AtlasRelationshipType.USES, []
        )
        for rel in sorted(uses, key=lambda x: x.target):
            software = atlas_data.software[rel.target]
            software_used_rows.append(
                {
                    "case study ID": case_study.id,
                    "case study name": case_study.name,
                    "source type": "case-study",
                    "source ID": case_study.id,
                    "source name": case_study.name,
                    "target software ID": software.id,
                    "target software name": software.name,
                    "description": rel.description or "",
                }
            )

    case_studies_df = pd.DataFrame(case_study_rows)
    techniques_used_df = pd.DataFrame(techniques_used_rows)
    entities_attributed_df = pd.DataFrame(entities_attributed_rows)
    if not techniques_used_df.empty:
        techniques_used_df = techniques_used_df.sort_values(
            ["case study ID", "step ID", "target technique ID"]
        )
    if not entities_attributed_df.empty:
        entities_attributed_df = entities_attributed_df.sort_values(
            ["case study ID", "target entity ID"]
        )
    return (
        case_studies_df,
        techniques_used_df,
        entities_attributed_df,
        pd.DataFrame(entities_reporting_rows),
        pd.DataFrame(software_used_rows),
    )


def _attack_reference_fields(
    attack_reference: schemas.AttackReference | None,
) -> dict[str, str]:
    if attack_reference is None:
        return {"ATT&CK ID": "", "ATT&CK URL": ""}
    return {
        "ATT&CK ID": attack_reference.id,
        "ATT&CK URL": str(attack_reference.url),
    }


def _build_entity_dataframes(
    atlas_data: schemas.AtlasExport,
    atlas_url: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    entity_rows = []
    techniques_used_rows = []
    software_used_rows = []

    for entity in sorted(atlas_data.entities.values(), key=lambda x: x.id):
        entity_rows.append(
            {
                "ID": entity.id,
                "name": entity.name,
                "description": entity.description,
                "url": _atlas_object_url(atlas_url, entity.id),
                "created": _format_date(entity.created_date),
                "last modified": _format_date(entity.modified_date),
                "entity type": entity.entity_type.value,
                "associated entities": "; ".join(
                    associated_entity.name
                    + (
                        f": {associated_entity.description}"
                        if associated_entity.description
                        else ""
                    )
                    for associated_entity in entity.associated_entities
                ),
                **_attack_reference_fields(entity.attack_reference),
                "references": _format_references(entity.references),
            }
        )

        uses = atlas_data.relationships.get(entity.id, {}).get(
            AtlasRelationshipType.USES, []
        )
        for rel in sorted(uses, key=lambda x: x.target):
            common = {
                "entity ID": entity.id,
                "entity name": entity.name,
                "entity type": entity.entity_type.value,
                "source type": "entity",
                "source ID": entity.id,
                "source name": entity.name,
                "description": rel.description or "",
            }
            if technique := atlas_data.techniques.get(rel.target):
                techniques_used_rows.append(
                    {
                        **common,
                        "target technique ID": technique.id,
                        "target technique name": technique.name,
                        "activity purpose": rel.activity_purpose.value
                        if rel.activity_purpose
                        else "",
                    }
                )
            elif software := atlas_data.software.get(rel.target):
                software_used_rows.append(
                    {
                        **common,
                        "target software ID": software.id,
                        "target software name": software.name,
                        "target software type": software.software_type.value,
                    }
                )

    return (
        pd.DataFrame(entity_rows),
        pd.DataFrame(techniques_used_rows),
        pd.DataFrame(software_used_rows),
    )


def _build_software_dataframes(
    atlas_data: schemas.AtlasExport,
    atlas_url: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    software_rows = []
    techniques_implemented_rows = []

    for software in sorted(atlas_data.software.values(), key=lambda x: x.id):
        software_rows.append(
            {
                "ID": software.id,
                "name": software.name,
                "description": software.description,
                "url": _atlas_object_url(atlas_url, software.id),
                "created": _format_date(software.created_date),
                "last modified": _format_date(software.modified_date),
                "software type": software.software_type.value,
                "software categories": ", ".join(
                    software.model_dump(mode="json")["software_categories"]
                ),
                "aliases": ", ".join(software.aliases),
                **_attack_reference_fields(software.attack_reference),
                "references": _format_references(software.references),
            }
        )

        implements = atlas_data.relationships.get(software.id, {}).get(
            AtlasRelationshipType.IMPLEMENTS, []
        )
        for rel in sorted(implements, key=lambda x: x.target):
            technique = atlas_data.techniques.get(rel.target)
            if technique is None:
                continue
            techniques_implemented_rows.append(
                {
                    "software ID": software.id,
                    "software name": software.name,
                    "software type": software.software_type.value,
                    "source type": "software",
                    "source ID": software.id,
                    "source name": software.name,
                    "target technique ID": technique.id,
                    "target technique name": technique.name,
                    "description": rel.description or "",
                }
            )

    return pd.DataFrame(software_rows), pd.DataFrame(techniques_implemented_rows)


def _build_matrix_df(atlas_data: schemas.AtlasExport) -> pd.DataFrame:
    relationships = atlas_data.relationships
    sequence_rels = relationships.get(ATLAS_MATRIX_ID, {}).get(
        AtlasRelationshipType.SEQUENCES, []
    )
    ordered_tactic_ids = [
        rel.target for rel in sorted(sequence_rels, key=lambda rel: rel.position or 0)
    ]
    if not ordered_tactic_ids:
        ordered_tactic_ids = sorted(atlas_data.tactics.keys())

    tactic_to_techniques: dict[str, set[str]] = defaultdict(set)
    parent_by_subtechnique: dict[str, str] = {}
    for source, rels_by_type in relationships.items():
        for rel in rels_by_type.get(AtlasRelationshipType.ACHIEVES, []):
            tactic_to_techniques[rel.target].add(source)
        for rel in rels_by_type.get(AtlasRelationshipType.SPECIALIZES, []):
            parent_by_subtechnique[rel.source] = rel.target

    subtechniques_by_parent: dict[str, list[str]] = defaultdict(list)
    for subtechnique, parent in parent_by_subtechnique.items():
        subtechniques_by_parent[parent].append(subtechnique)
    for parent in subtechniques_by_parent:
        subtechniques_by_parent[parent].sort(
            key=lambda technique_id: (
                atlas_data.techniques[technique_id].name
                if technique_id in atlas_data.techniques
                else technique_id
            )
        )

    column_data: list[tuple[str, list[str]]] = []
    max_rows = 0

    for tactic_id in ordered_tactic_ids:
        tactic = atlas_data.tactics.get(tactic_id)
        if not tactic:
            continue

        top_level = sorted(
            [
                technique_id
                for technique_id in tactic_to_techniques.get(tactic_id, set())
                if technique_id in atlas_data.techniques
                and technique_id not in parent_by_subtechnique
            ],
            key=lambda technique_id: atlas_data.techniques[technique_id].name,
        )

        super_column: list[str] = []
        sub_column: list[str] = []
        has_sub = False
        for parent_id in top_level:
            parent_name = atlas_data.techniques[parent_id].name
            children = [
                child_id
                for child_id in subtechniques_by_parent.get(parent_id, [])
                if child_id in atlas_data.techniques
            ]
            if children:
                has_sub = True
                for idx, child_id in enumerate(children):
                    super_column.append(parent_name if idx == 0 else "")
                    sub_column.append(atlas_data.techniques[child_id].name)
            else:
                super_column.append(parent_name)
                sub_column.append("")

        if not has_sub:
            column_data.append((tactic.name, super_column))
        else:
            column_data.append((tactic.name, super_column))
            column_data.append(("", sub_column))

        max_rows = max(max_rows, len(super_column))

    matrix_dict: dict[str, list[str]] = {}
    for idx, (header, values) in enumerate(column_data):
        key = header if header else f"__blank_{idx}"
        matrix_dict[key] = values + [""] * (max_rows - len(values))

    if column_data and column_data[-1][0] != "":
        tail_values = [""] * max_rows
        if tail_values:
            tail_values[0] = "_"
        matrix_dict["__tail_blank__"] = tail_values

    matrix_df = pd.DataFrame(matrix_dict)
    matrix_df.columns = [
        header if not header.startswith("__blank_") else ""
        for header in matrix_df.columns
    ]
    return matrix_df


def _autosize(writer: pd.ExcelWriter, sheet_name: str, frame: pd.DataFrame) -> None:
    worksheet = writer.sheets[sheet_name]
    for col_idx, col_name in enumerate(frame.columns):
        col_values = frame.iloc[:, col_idx].fillna("").astype(str)
        width = max(
            len(str(col_name)), col_values.map(len).max() if len(col_values) else 0
        )
        worksheet.set_column(col_idx, col_idx, min(max(width + 2, 12), 80))


def _format_matrix_sheet(writer: pd.ExcelWriter, frame: pd.DataFrame) -> None:
    worksheet = writer.sheets["matrix"]
    book = writer.book

    tactic_header_fmt = book.add_format(
        {"bold": True, "border": 1, "align": "center", "valign": "vcenter"}
    )
    left_border_fmt = book.add_format({"left": 1})
    right_border_fmt = book.add_format({"right": 1})
    both_border_fmt = book.add_format({"left": 1, "right": 1})

    widths: list[int] = []
    for col_idx, col_name in enumerate(frame.columns):
        col_values = frame.iloc[:, col_idx].fillna("").astype(str)
        width = max(
            len(str(col_name)), col_values.map(len).max() if len(col_values) else 0
        )
        widths.append(min(max(width + 2, 12), 80))

    headers = list(frame.columns)
    col = 0
    while col < len(headers):
        header = headers[col]
        if not header or header == "__tail_blank__":
            col += 1
            continue

        has_subtech_column = col + 1 < len(headers) and headers[col + 1] == ""
        end_col = col + 1 if has_subtech_column else col

        if has_subtech_column:
            worksheet.merge_range(0, col, 0, end_col, header, tactic_header_fmt)
        else:
            worksheet.write(0, col, header, tactic_header_fmt)

        if col == end_col:
            worksheet.set_column(col, col, widths[col], both_border_fmt)
        else:
            worksheet.set_column(col, col, widths[col], left_border_fmt)
            worksheet.set_column(end_col, end_col, widths[end_col], right_border_fmt)

        col = end_col + 1


def _write_workbook(path: Path, sheets: list[tuple[str, pd.DataFrame]]) -> None:
    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        for sheet_name, frame in sheets:
            frame.to_excel(writer, sheet_name=sheet_name, index=False)
            if sheet_name == "matrix" and "__tail_blank__" in frame.columns:
                worksheet = writer.sheets[sheet_name]
                tail_col = list(frame.columns).index("__tail_blank__")
                blank_fmt = writer.book.add_format({})
                worksheet.write_blank(0, tail_col, None, blank_fmt)
                worksheet.write_blank(1, tail_col, None, blank_fmt)
            _autosize(writer, sheet_name, frame)
            if sheet_name == "matrix":
                _format_matrix_sheet(writer, frame)


def export_to_excel(
    input_path: Path,
    output_dir: Path,
    prefix: str = "atlas",
    atlas_url: str = "https://atlas.mitre.org",
) -> list[Path]:
    atlas_data = _load_data(input_path)

    techniques_df = _build_techniques_df(atlas_data, atlas_url)
    tactics_df = _build_tactics_df(atlas_data, atlas_url)
    mitigations_df, techniques_addressed_df = _build_mitigation_dataframes(
        atlas_data, atlas_url
    )
    (
        case_studies_df,
        case_study_techniques_df,
        case_study_entities_df,
        case_study_reporters_df,
        case_study_software_df,
    ) = _build_case_study_dataframes(atlas_data, atlas_url)
    entities_df, entity_techniques_df, entity_software_df = _build_entity_dataframes(
        atlas_data, atlas_url
    )
    software_df, software_techniques_df = _build_software_dataframes(
        atlas_data, atlas_url
    )
    matrix_df = _build_matrix_df(atlas_data)

    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "master": output_dir / f"{prefix}.xlsx",
        "techniques": output_dir / f"{prefix}-techniques.xlsx",
        "tactics": output_dir / f"{prefix}-tactics.xlsx",
        "mitigations": output_dir / f"{prefix}-mitigations.xlsx",
        "case_studies": output_dir / f"{prefix}-case-studies.xlsx",
        "entities": output_dir / f"{prefix}-entities.xlsx",
        "software": output_dir / f"{prefix}-software.xlsx",
        "matrices": output_dir / f"{prefix}-matrices.xlsx",
    }

    _write_workbook(
        outputs["master"],
        [
            ("techniques", techniques_df),
            ("tactics", tactics_df),
            ("mitigations", mitigations_df),
            ("case studies", case_studies_df),
            ("entities", entities_df),
            ("software", software_df),
            ("matrix", matrix_df),
        ],
    )
    _write_workbook(outputs["techniques"], [("techniques", techniques_df)])
    _write_workbook(outputs["tactics"], [("tactics", tactics_df)])
    _write_workbook(
        outputs["mitigations"],
        [
            ("mitigations", mitigations_df),
            ("techniques addressed", techniques_addressed_df),
        ],
    )
    _write_workbook(
        outputs["case_studies"],
        [
            ("case studies", case_studies_df),
            ("techniques used", case_study_techniques_df),
            ("entities attributed", case_study_entities_df),
            ("entities reporting", case_study_reporters_df),
            ("software used", case_study_software_df),
        ],
    )
    _write_workbook(
        outputs["entities"],
        [
            ("entities", entities_df),
            ("techniques used", entity_techniques_df),
            ("software used", entity_software_df),
        ],
    )
    _write_workbook(
        outputs["software"],
        [
            ("software", software_df),
            ("techniques implemented", software_techniques_df),
        ],
    )
    _write_workbook(outputs["matrices"], [("matrix", matrix_df)])

    return list(outputs.values())


def main() -> None:
    parser = ArgumentParser(description="Generate ATLAS Excel workbooks from YAML data")
    parser.add_argument(
        "-i",
        type=Path,
        dest="atlas_data_filepath",
        default=Path("dist/ATLAS-latest.yaml"),
        help="Path to ATLAS YAML data",
    )
    parser.add_argument(
        "-o",
        type=Path,
        dest="output_dir",
        default=Path("dist/excel-files"),
        help="Directory for generated XLSX files",
    )
    parser.add_argument("--prefix", type=str, default="atlas", help="Filename prefix")
    parser.add_argument(
        "--atlas-url",
        type=str,
        default="https://atlas.mitre.org",
        help="Base URL used for object URL columns",
    )
    args = parser.parse_args()

    created = export_to_excel(
        args.atlas_data_filepath, args.output_dir, args.prefix, args.atlas_url
    )
    for path in created:
        print(path)


if __name__ == "__main__":
    main()
