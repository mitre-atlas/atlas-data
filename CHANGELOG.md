# ATLAS Data Changelog

## [3.0.0]() (2022-??-??)

Move to new GitHub repository

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

## [2.3.0]() (2022-01-21)

#### Case studies
- Added new case study
    1. AML.CS0015
- Added key `incident-date-granularity` with values `DATE`, `MONTH`, or `YEAR` indicating the specificity of the `incident-date`

## [2.2.1]() (2021-12-08)

Fixes to all data

#### Tests
- Added pytest suite for data validation and syntax checks

## [2.2.0]() (2021-10-29)

Standalone data

#### Tactics and techniques
- Adapted referenced ATT&CK tactics into the ATLAS framework
    + Updated descriptions to be machine learning-specific
    + Changed IDs to ATLAS IDs
- Added ATLAS techniques used in new case studies, adapted from ATT&CK with updated ATLAS IDs and descriptions
    + Data from Information Repositories
    + Establish Accounts
    + Valid Accounts

#### Case studies
- Added new case studies
    1. AML.CS0013
    2. AML.CS0014

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
