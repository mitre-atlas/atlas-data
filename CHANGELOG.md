# ATLAS Data Changelog

## [4.3.0]() (2023-02-28)

New case study on prompt injection and adapted new associated techniques from ATT&CK.

#### Tactics and techniques
- Added new techniques
  + [Exploit Public-Facing Application](https://atlas.mitre.org/techniques/AML.T0049)
  + [Command and Scripting Interpreter](https://atlas.mitre.org/techniques/AML.T0050)


#### Case studies
- Added new case study
  + [Achieving Code Execution in MathGPT via Prompt Injection](https://atlas.mitre.org/studies/AML.CS0016)

## [4.2.0]() (2023-01-18)

Denotes existing tactics and techniques adapted from ATT&CK and adds a new case study on a dependency confusion.

#### Tactics and techniques
- Added new technique
  + [Data from Local System](https://atlas.mitre.org/techniques/AML.T0037)
- ATLAS objects that are adapted from ATT&CK are denoted by the additional key `ATT&CK-reference`, ex.
  + ```
    ATT&CK-reference:
      id: T1595
      url: https://attack.mitre.org/techniques/T1595/
    ```

#### Case studies
- Added new case study
  + [Compromised PyTorch Dependency Chain](https://atlas.mitre.org/studies/AML.CS0015)


## [4.1.0]() (2022-10-27)

Refreshed existing case studies

#### Tactics and techniques
- Added a ATLAS technique
    + [System Misuse for External Effect](https://atlas.mitre.org/techniques/AML.T0048)
- Updated descriptions

#### Case studies
- Updated existing case study content
- New case study fields: case study type (exercise or incident), actor, target, and reporter

#### Tests
- Added test for mismatched tactics and techniques in case study procedure steps

## [4.0.1]() (2022-07-12)

#### Tools
- Output script checks for valid YAML file formats

#### Tests
- Added test for duplicate data object IDs

## [4.0.0]() (2022-05-27)

Support for defining multiple matrices

#### Distributed files
- `ATLAS.yaml` has a new top-level key `matrices` containing a list of matrix names, tactics, techniques, and other associated data objects
  + The `tactics` and `techniques` keys that was previously at the top-level of this file have been moved into an entry of this `matrices` key
  + Note that case studies remains at the top-level, as they can contain techniques from multiple matrices
- Updated schema files for the new format

#### Data
- New data definition file `data.yaml` containing top-level metadata, data objects, and paths to included matrix data

#### Tools
- Case study import script improvements and support for output format changes

## [3.1.0]() (2022-05-16)

Users can define custom data object types

#### Distributed files
- Case study JSON schema accepts extra top-level keys

#### Schemas
- Relaxed ID prefix patterns
  + Must start with a prefix of capital letter(s), optionally followed by numbers, then a "." (ex. AML.)
  + Optionally can repeat the above pattern (ex. AML.VER123. )
  + Ending in the expected pattern for the data object (ex. AML.VER123.T1234 )
- Introduced a mitigation object schema for testing `object-type: "mitigation"` data, if exists
- Optional case study references, if exists, expected to be a list

#### Tools
- Updated output YAML generation script to accept arbitrary object types and output them as top-level keys.
  + Ex. `object-type: "mitigation"` produces the top-level key `mitigations:` in `ATLAS.yaml`
- Case study import script can replace existing case studies when provided files with an existing ID

## [3.0.0]() (2022-03-23)

Move to new GitHub repository under the `mitre-atlas` group

#### Distributed files
- Renamed case study JSON schema file and updated to include `study` key expected by the ATLAS website
- Added README.md with usage

#### Case studies
- Minor title updates

## [2.4.0]() (2022-03-10)

Repository re-org and cleanup, added READMEs to all directories

#### Distributed files
- Moved `ATLAS.yaml` into a new `dist` directory
- Added JSON Schema files for `ATLAS.yaml` and case study files as created by the ATLAS website to `dist/schemas` directory

#### Schemas
- Moved schemas from test fixtures into their own directory

#### Tools
- Moved Navigator scripts to a separate repository
- Added case study file import script
- Added JSON Schema generation script

## [2.3.1]() (2022-02-07)

#### Tools
- ATLAS YAML generation script uses Jinja template evaluation and handles relative `!include` filepaths

## [2.3.0]() (2022-01-24)

#### Tactics and techniques
- Adapted referenced ATT&CK tactics into the ATLAS framework
    + Updated descriptions to be machine learning-specific
    + Changed IDs to ATLAS IDs
- Added ATLAS techniques used in new case studies, adapted from ATT&CK with updated ATLAS IDs and descriptions
    + Data from Information Repositories
    + Establish Accounts
    + Valid Accounts

#### Case studies
- Added key `incident-date-granularity` to case study files with values `DATE`, `MONTH`, or `YEAR` indicating the specificity of the `incident-date`

## [2.2.1]() (2021-12-08)

Fixes to all data

#### Tests
- Added pytest suite for data validation and syntax checks

## [2.2.0]() (2021-10-29)

#### Case studies
- Added new case studies
    1. [Backdoor Attack on Deep Learning Models in Mobile Apps](https://atlas.mitre.org/studies/AML.CS0013)
    2. [Confusing Antimalware Neural Networks](https://atlas.mitre.org/studies/AML.CS0014)

#### Tools
- Removed retrieval and usage of ATT&CK Enterprise data

## [2.1.0]() (2021-08-31)

`advmlthreatmatrix` renamed to `ATLAS`

- Scripts updated accordingly
- Fixes to all data

## [2.0.1]() (2021-06-11)

Fixes to all data

#### Tools
- Added data validation script

## [2.0.0]() (2021-05-13)

#### Distributed files
- Added `ATLAS.yaml` file with all tactics, techniques, and case studies

#### Tactics and techniques
- Removed hardcoded IDs in favor of YAML anchors and template syntax

#### Tools
- Added `ATLAS.yaml` generation script
- Added ATT&CK Enterprise v9 STIX retrieval and conversion script

## [1.0.0]() (2021-02-17)

Initial data definition
