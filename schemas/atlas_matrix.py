from datetime import datetime
import json

from schema import Literal, Or, Schema

from .atlas_obj import (
    tactic_schema,
    technique_schema,
    subtechnique_schema,
    case_study_schema
)

"""Describes the ATLAS.yaml schema, which corresponds to data/matrix.yaml."""

atlas_matrix_schema = Schema(
    {
        "id": str,
        "name": str,
        "version": Or(str, int, float),
        "tactics": [
            tactic_schema
        ],
        "techniques": [
            Or(technique_schema, subtechnique_schema)
        ],
        "case-studies": [
            case_study_schema
        ]
    },
    name='ATLAS Matrix Schema',
    ignore_extra_keys=True,
    description=f'Generated on {datetime.now().strftime("%Y-%m-%d")}'
)
