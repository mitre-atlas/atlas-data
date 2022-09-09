# ATLAS Website Case Study Schema

*Generated on 2022-06-03*

## Properties

- **`study`** *(object)*: Can contain additional properties.
  - **`name`** *(string)*
  - **`summary`** *(string)*
  - **`incident-date`** *(string)*
  - **`incident-date-granularity`**: Must be one of: `['YEAR', 'MONTH', 'DATE']`.
  - **`procedure`** *(array)*
    - **Items** *(object)*: Can contain additional properties.
      - **`tactic`**: Refer to *#/definitions/id_tactic*.
      - **`technique`**
      - **`description`** *(string)*
  - **`reporter`** *(string)*
  - **`target`** *(string)*
  - **`actor`** *(string)*
  - **`case-study-type`**: Must be one of: `['incident', 'exercise']`.
  - **`references`**
  - **`id`**: Refer to *#/definitions/id_case_study*.
  - **`object-type`**
- **`meta`** *(object)*: Can contain additional properties.
## Definitions

- **`id_tactic`** *(string)*
- **`id_technique`** *(string)*
- **`id_subtechnique`** *(string)*
- **`id_case_study`** *(string)*
