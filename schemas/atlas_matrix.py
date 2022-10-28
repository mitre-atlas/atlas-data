from datetime import datetime
import json

from schema import Optional, Or, Schema

from .atlas_obj import (
    tactic_schema,
    technique_schema,
    subtechnique_schema,
    case_study_schema
)

"""Describes the matrix.yaml matrix schema and the ATLAS.yaml output schema."""

atlas_matrix_schema = Schema(
    {
        "id": str,
        "name": str,
        "tactics": [
            tactic_schema
        ],
        "techniques": [
            Or(technique_schema, subtechnique_schema)
        ]
    },
    name='ATLAS Matrix Schema',
    ignore_extra_keys=True
)

atlas_output_schema = Schema(
    {
        "id": str,
        "name": str,
        "version": Or(str, int, float),
        "matrices": [
            atlas_matrix_schema
        ],
        Optional("case-studies"): [
            case_study_schema
        ]
    },
    name='ATLAS Output Schema',
    ignore_extra_keys=True,
    description=f'Generated on {datetime.now().strftime("%Y-%m-%d")}'
)
