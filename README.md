# MITRE ATLAS Data

This repository distributes data for [MITRE ATLAS&trade;](https://atlas.mitre.org/) (Adversarial Threat Landscape for AI Systems), a public knowledge base of adversary TTPs targeting AI systems.

It includes the supporting tooling for parsing, validating, and managing ATLAS data.

The ATLAS YAML files in this repository are the authoritative source of ATLAS data. The database and REST API support authoring updates to those files: import YAML into a working database, edit through the API, and export YAML for review and inclusion in the repository.

## Quick Start with ATLAS Data

Install uv: https://docs.astral.sh/uv/getting-started/installation/

Install dependencies:
```bash
uv sync --dev
```

Activate virtual environment:
```bash
source .venv/bin/activate
```

Parse and validate ATLAS data in Python:
```python
import yaml
from pathlib import Path
from atlas.schemas import AtlasExport

path = Path("dist/ATLAS-latest.yaml")

with path.open("r") as f:
    raw = yaml.safe_load(f)

atlas_data = AtlasExport.model_validate(raw)

print("Release version:", atlas_data.collection.version)
print("Tactics:", len(atlas_data.tactics))
print("Techniques:", len(atlas_data.techniques))
print("Mitigations:", len(atlas_data.mitigations))
print("Relationships:", len(atlas_data.relationships))
```

## Project layout

- `dist/` - distributed ATLAS data files and the release manifest.
- `atlas/` - ATLAS Python package containing Pydantic schemas and REST API
- `tools/` - command-line tooling to populate ATLAS YAML into the database and generate additional distribution formats (STIX, Navigator layers, Excel).
- `tests/` - test suite for ATLAS data and REST API
- `.github/workflows/` - CI workflows for release asset generation

## Generate Attack Flows

Generate one STIX 2.1 Attack Flow bundle for every case study:

```bash
uv run generate-attack-flows -i dist/ATLAS-latest.yaml -o dist/attack-flows
```

The generator is also a standalone `uv` script and can be run directly:

```bash
uv run tools/generate_attack_flows.py -i dist/ATLAS-latest.yaml -o dist/attack-flows
```

Select specific case studies by repeating `--case-study`:

```bash
uv run generate-attack-flows --case-study AML.CS0000
```

The generated flow preserves each case study's authored `leads-to` graph,
including branches and repeated uses of a technique.


## Distributed ATLAS Data

The latest ATLAS data is stored in `dist/ATLAS-latest.yaml`

### Versioning

ATLAS releases monthly content updates. It follows two versioning schemes:

- **Content version**: data content version in `collection.version` that follows YYYY.MM.N versioning (e.g. `2026.05`).
- **Format version**: data format version in `format-version` that follows semantic versioning (e.g. `6.0.0`).

`dist/manifest.yaml` ties these together by listing which file path implements which format-version for each release.

Note: separating content from format versions started with 2026.05 / 6.0.0. Previously content and format changes followed combined SEMVER versioning.

### Distributed Versions

A summary of distributed ATLAS YAML files:

- `dist/ATLAS-latest.yaml` will always point to the latest content in the latest format.
- `dist/v6/ATLAS-latest.yaml` will always point to the latest content in v6 format.
- `dist/v6/ATLAS-{version}.yaml` contain historical versions of ATLAS migrated to v6 format.
- `dist/legacy/ATLAS-{version}.yaml` contain historical versions of ATLAS in their original format at time of release.
- `dist/ATLAS.yaml` is deprecated and will no longer be updated.

The manifest (`dist/manifest.yaml`) contains a complete listing of distributed files. It maps each content release to one or more files by `format-version`.

## ATLAS Data Format

Current distributable ATLAS format is represented by `atlas.schemas.AtlasExport`.

### Primary ATLAS objects

ATLAS objects share an ID, name, description, references, and creation and
modification dates. Relationships connect the objects within a content version.

#### Collection

A **Collection** identifies a versioned release of ATLAS content. It records the
release's `version` and descriptive metadata. Each export includes one Collection,
alongside the objects and relationships that make up that release.

#### Matrix

A **Matrix** defines the ordered presentation of tactics. Its `sequences`
relationships assign each tactic a position in the matrix. Techniques appear under
tactics through their `achieves` relationships. Matrix order is a presentation
order; the procedure sequence for a specific activity is recorded in a Case Study.

#### Tactic

A **Tactic** describes the objective, or "why," behind an activity, such as
Reconnaissance. A technique connects to a tactic through an `achieves` relationship.
The same technique can support multiple tactical objectives. Tactics can also carry
an external ATT&CK reference where applicable.

#### Technique and sub-technique

A **Technique** describes a reusable method for carrying out an activity: the
"how" associated with one or more tactical objectives. Its `platforms` identify
applicable environments (`Predictive AI`, `Generative AI`, `Agentic AI`, or
`Enterprise`), and its `maturity` records the authored assessment of the supporting
evidence (`Feasible`, `Demonstrated`, or `Realized`).

A **sub-technique** describes a more specific form of a parent technique. It uses
the same Technique object type and connects to its parent through `specializes`.
Case Studies document specific applications of techniques; Software can implement
them, Entities can use them, and Mitigations can address them.

#### Mitigation

A **Mitigation** describes a defensive measure that can prevent, limit, or reduce
the impact of activity represented by one or more techniques. Its `mitigates`
relationships identify the techniques it addresses.

Mitigations have `categories` (`Policy`, `Technical - AI`, or `Technical - Cyber`)
and `lifecycle-phases` identifying where they apply across the AI lifecycle, from
business and data understanding through deployment, monitoring, and maintenance.
These fields help users identify relevant defensive measures for their work.

#### Case Study

A **Case Study** documents a specific instance of activity and the evidence for
how techniques were applied. Its `type` is `Incident` for a real-world occurrence
or `Exercise` for a deliberate demonstration or evaluation. Its dates describe
the represented period, with explicit year, month, or day precision; an omitted
end date represents an ongoing period.

In API payloads, `attack-chain` contains procedure steps. In exports, those steps
are `employs` relationships to techniques, with tactic context, `step-id`,
`leads-to`, and descriptions. A technique may appear in multiple steps.
`attributed-to` links identify Entities associated with the documented activity
and record its `activity-purpose`. Free-text `actor` can retain unresolved or
additional attribution context, while `target` describes what was affected.
Incident reporting credit is recorded separately through `reporter` and optional
`reported-by` links; see [Reporting provenance](#reporting-provenance).

#### Entity

An **Entity** is a reusable identity supported by source evidence. Its `entity-type`
is `Activity Cluster`, `Organization`, `Team`, or `Individual`; `associated-entities`
records other tracking designations and any qualification about the association.
Entity is broader than an ATT&CK Group. External ATT&CK Group IDs (`G####`) and
references retain ATT&CK terminology and are distinct from ATLAS Entity IDs.

Identity type does not imply intent. A security team or organization can conduct
an adversarial operation or security evaluation; `activity-purpose` records the
documented activity on an attribution or technique-use relationship.

Security teams remain eligible Entities. Their relationships provide attribution,
credit, discovery of related evaluations, and visibility into whether evidence is
concentrated in one team rather than independently corroborated.

#### Software

A **Software** object identifies a reusable computational implementation, including
programs, libraries, models, services, agents, integrations, and prompt packages.
Its `software-type` is `Tool` or `Malware`. Software connects to the
techniques it implements through `implements`; an Entity's `uses` relationship
can identify its use of that Software. Its `aliases` field provides alternative names
for the same implementation. Software also has `software-categories` labels that
include `program`, `library`, `model`, `service`, `ai-agent`, `ai-agent-framework`,
`ai-agent-integration`, and `prompt-package`.

The Software object describes the implementation, the Entity identifies an
operator, and the Technique describes the method. Software may carry an external
ATT&CK reference where applicable.

### Export structure

Top-level keys:

- `format-version`
- `collection`
- `matrix`
- `tactics`
- `techniques`
- `mitigations`
- `case-studies`
- `entities`
- `software`
- `relationships`

High-level shape (abbreviated):

```yaml
format-version: 6.1.0

collection:
  id: ATLAS-collection
  version: "2026.05"
  name: ATLAS
  description: Adversarial Threat Landscape for AI Systems

matrix:
  id: ATLAS-matrix
  name: ATLAS

tactics:
  AML.TA0002:
    id: AML.TA0002
    object-type: tactic
    name: Reconnaissance

techniques:
  AML.T0005:
    id: AML.T0005
    object-type: technique
    maturity: Demonstrated
    platforms:
      - Predictive AI

mitigations:
  AML.M0001:
    id: AML.M0001
    object-type: mitigation

case-studies:
  AML.CS0001:
    id: AML.CS0001
    object-type: case-study
    type: Incident

relationships:
  ATLAS-matrix:
    sequences: [...]
  AML.T0005:
    achieves: [...]
  AML.M0001:
    mitigates: [...]
  AML.CS0001:
    employs: [...]
```

### ID conventions

The format enforces typed ID patterns, including:

- Collection ID: `ATLAS-collection`
- Matrix ID: `ATLAS-matrix`
- Tactic ID: `AML.TA####`
- Technique ID: `AML.T####`
- Sub-technique ID: `AML.T####.###`
- Mitigation ID: `AML.M####`
- Case study ID: `AML.CS####`
- Entity ID: `AML.E####`
- Software ID: `AML.S####`

### Relationship types

ATLAS object relationships are explicit and typed:

- `sequences`: matrix -> tactic (ordered matrix layout)
- `achieves`: technique -> tactic
- `specializes`: sub-technique -> parent technique
- `mitigates`: mitigation -> technique
- `employs`: case study -> technique (includes `tactic`, `step-id`, `leads-to` metadata)
- `attributed-to`: case study -> entity (requires `activity-purpose`)
- `reported-by`: Incident case study -> entity (optional reporting provenance)
- `uses`: entity -> technique or software
- `implements`: software -> technique

### Reporting provenance

Case Studies permanently retain free-text `reporter` as source credit. Optional
`reported-by` links enable canonical lookup, including multiple reporters and
Entities that are both actors and reporters. Both reporting representations are
Incident-only. Neither is inferred from or synchronized with the other, and
reporting never implies attribution or changes technique maturity.

API request/response example (excerpt):

```yaml
reporter: OpenAI, Hugging Face
reported-by:
  - entity: AML.E0044
  - entity: AML.E0048
attributed-to:
  - entity: AML.E0044
    activity-purpose: Unintended Consequence
```

YAML exports keep these links in the flat `relationships` section:

```yaml
relationships:
  AML.CS0068:
    reported-by:
      - source: AML.CS0068
        target: AML.E0048
        relationship-type: reported-by
```

Relationship lists follow full-replacement PUT semantics: send the lists to retain
when updating a case study; omitted lists default to empty. Reporter text is a
separate field. Deleting an Entity removes its links but preserves reporter text.
See [reporter curation decisions](docs/reporter-entity-review.md) for current links
and unresolved identities.

## REST API

### Technique maturity

Technique maturity is an authored assessment (`Feasible`, `Demonstrated`, or
`Realized`). The API defaults new techniques to `Feasible` and preserves maturity
when it is omitted from an update. Relationship edits, imports, and version copies
preserve the authored value.

Publication minimums are validated by `tests/test_data.py`:

- Exercise case studies and Security Evaluation entity usage require at least
  `Demonstrated`.
- Incident case studies and Adversarial Operation or Unintended Consequence entity
  usage require `Realized`.
- Parent techniques must be at least as mature as each sub-technique.

These checks allow editorial elevations above the relationship-derived minimum.
They apply to case-study `employs` and entity-to-technique `uses` relationships;
attribution, reporting, and software relationships do not impose a maturity minimum.

Validate the current release (defaults to `dist/v6/ATLAS-latest.yaml`):

```bash
uv run pytest tests/test_data.py
```

To validate a specific exported dataset:

```bash
ATLAS_DATA_FILE=dist/v6/ATLAS-2026.10.yaml uv run pytest tests/test_data.py
```

The Generate Release Assets workflow runs these checks on the requested release's
versioned YAML before generating any assets.

The REST API is an authoring tool for the authoritative ATLAS YAML files. The authoring workflow is:

1. Import a v6 ATLAS YAML file into the database as a working copy.
2. Make edits through the REST API.
3. Export the updated data to YAML.
4. Review and validate the exported YAML, then include the approved changes in the repository for distribution.

The API is backed by a SQLite database stored at `sqlite:///./atlas.db`. This database holds the authoring working copy; the repository's YAML files remain the source of record. API edits must be exported and incorporated into those files to become part of the authoritative data.

### Quick Start with the API

Install uv: https://docs.astral.sh/uv/getting-started/installation/

Install dependencies:
```bash
uv sync
```

Activate virtual environment:
```bash
source .venv/bin/activate
```

Load ATLAS data into the database (automatically initializes or upgrades the schema):
```bash
uv run populate-atlas-db -i dist/ATLAS-latest.yaml
```

Run API locally:
```bash
uv run fastapi run atlas/api.py --reload
```

It is now possible to browse the api docs at http://localhost:8000/docs

Export the data from the API:
```bash
curl http://localhost:8000/versions/2026.05/data -o ATLAS-export.yaml
```

### Database upgrades

`populate-atlas-db` automatically runs all pending schema revisions before importing
data. To initialize or upgrade the database separately before starting the API:

```bash
uv run alembic upgrade head
```

This command initializes an empty database and upgrades databases previously
created by Alembic. Existing databases without an `alembic_version` table are
unsupported and cannot be upgraded automatically. Back up and recreate an
unversioned local database, then reload its data from an ATLAS YAML export:

```bash
mv atlas.db atlas.db.backup
uv run alembic upgrade head
uv run populate-atlas-db -i dist/ATLAS-latest.yaml
```

### REST API Endpoints

- health:
  - `GET /health`
- version management:
  - `POST /versions`
  - `GET /versions`
  - `GET /versions/{version}`
  - `PATCH /versions/{version}`
  - `DELETE /versions/{version}`
  - `GET /versions/{version}/data` (exports version as YAML)
- data management (version-scoped):
  - `/{version}/collection/`
  - `/{version}/matrix/`
  - `/{version}/tactics/`
  - `/{version}/techniques/`
  - `/{version}/mitigations/`
  - `/{version}/case-studies/`
   - `/{version}/entities/`
  - `/{version}/software/`

## Tools

Tools for generating downstream data formats.

### ATLAS to STIX

Entrypoint: `atlas-to-stix` (`tools/atlas_to_stix.py`)

Generate ATLAS STIX:
```bash
uv run tools/atlas_to_stix.py -i dist/v6/ATLAS-2026.05.yaml -o dist/stix-atlas.json
```

Generate ATLAS + ATT&CK Enterprise STIX bundle:
```bash
uv run tools/atlas_to_stix.py -i dist/v6/ATLAS-2026.05.yaml --include-attack -o dist/stix-atlas-attack-enterprise.json
```

Other options:
- `--include-case-studies`
- `--maturity-threshold {feasible,demonstrated,realized}`
- `--url`, `--source_name`, `--identity_name`

Activity Clusters become STIX Intrusion Sets; organizations, teams, and individuals
become STIX Identities. Software becomes STIX Malware or Tool. These objects use
standard STIX properties only; Activity Cluster associated names become native
Intrusion Set `aliases`, while their descriptions become named external references.

### ATLAS to Excel

Entrypoint: `atlas-to-excel` (`tools/atlas_to_excel.py`)

Generate ATLAS Excel workbooks:
```bash
uv run atlas-to-excel -i dist/v6/ATLAS-2026.05.yaml
```

Default output directory: `dist/excel-files/`

Entity records are in `atlas-entities.xlsx`. The case-study workbook retains the
`reporter` text column and has separate `entities attributed` and `entities reporting`
worksheets.

### Generate ATLAS Navigator layers

Entrypoint: `generate-navigator-layers` (`tools/generate_navigator_layers.py`)

Generate Navigator layers:
```bash
uv run generate-navigator-layers -i dist/v6/ATLAS-2026.05.yaml
```

Generated layers target ATT&CK Navigator 5.3.2, layer format 4.5, and the
custom `atlas-atlas` domain used by the ATLAS Navigator.

## Release Statement

©2021-2026 The MITRE Corporation. ALL RIGHTS RESERVED.
Approved for Public Release; Distribution Unlimited. Public Release Case Numbers 21-2363, 26-1162.
