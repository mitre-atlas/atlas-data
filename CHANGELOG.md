## [5.2.0]() (2025-12-24)

###### Techniques

- Added new techniques

  - [AI Service API](/techniques/AML.T0096)
  - [Virtualization/Sandbox Evasion](/techniques/AML.T0097)
  - [AI Agent Tool Credential Harvesting](/techniques/AML.T0098)
  - [AI Agent Tool Data Poisoning](/techniques/AML.T0099)
  - [AI Agent Clickbait](/techniques/AML.T0100)
  - [Data Destruction via AI Agent Tool Invocation](/techniques/AML.T0101)
  - [Generate Malicious Commands](/techniques/AML.T0102)

- Updated existing techniques

  - [Spamming AI System with Chaff Data](/techniques/AML.T0046)
  - [Prompt Infiltration via Public-Facing Application](/techniques/AML.T0093)
  - [LLM Prompt Obfuscation](/techniques/AML.T0068)
  - [Obtain Capabilities: Generative AI](/techniques/AML.T0016.002)
  - [Cloud Service Discovery](/techniques/AML.T0075)

###### Mitigations

- Added new mitigations

  - [Segmentation of AI Agent Components](/mitigations/AML.M0032)
  - [Input and Output Validation for AI Agent Components](/mitigations/AML.M0033)
  - [Deepfake Detection](/mitigations/AML.M0034)

- Updated existing mitigations

  - [Limit Public Release of Information](/mitigations/AML.M0000)
  - [Limit Model Artifact Release](/mitigations/AML.M0001)
  - [Passive Output Manipulation](/mitigations/AML.M0002)
  - [Model Hardening](/mitigations/AML.M0003)
  - [Restrict Number of AI Model Queries](/mitigations/AML.M0004)
  - [Control Access to AI Models and Data at Rest](/mitigations/AML.M0005)
  - [Use Ensemble Methods](/mitigations/AML.M0006)
  - [Sanitize Training Data](/mitigations/AML.M0007)
  - [Validate AI Model](/mitigations/AML.M0008)
  - [Use Multi-Modal Sensors](/mitigations/AML.M0009)
  - [Input Restoration](/mitigations/AML.M0010)
  - [Restrict Library Loading](/mitigations/AML.M0011)
  - [Encrypt Sensitive Information](/mitigations/AML.M0012)
  - [Code Signing](/mitigations/AML.M0013)
  - [Verify AI Artifacts](/mitigations/AML.M0014)
  - [Adversarial Input Detection](/mitigations/AML.M0015)
  - [Vulnerability Scanning](/mitigations/AML.M0016)
  - [AI Model Distribution Methods](/mitigations/AML.M0017)
  - [User Training](/mitigations/AML.M0018)
  - [Control Access to AI Models and Data in Production](/mitigations/AML.M0019)
  - [Generative AI Guardrails](/mitigations/AML.M0020)
  - [Generative AI Guidelines](/mitigations/AML.M0021)
  - [Generative AI Model Alignment](/mitigations/AML.M0022)
  - [AI Bill of Materials](/mitigations/AML.M0023)
  - [AI Telemetry Logging](/mitigations/AML.M0024)
  - [Maintain Dataset Provenenance](/mitigations/AML.M0025)
  - [Privileged AI Agent Permissions Configuration](/mitigations/AML.M0026)
  - [Single-User AI Agent Permissions Configuration](/mitigations/AML.M0027)
  - [AI Agent Tools Permissions Configuration](/mitigations/AML.M0028)
  - [Human In-the-Loop for AI Agent Actions](/mitigations/AML.M0029)
  - [Restrict AI Agent Tool Invocation on Untrusted Data](/mitigations/AML.M0030)

###### Case Studies

- Added new case studies

  - [SesameOp: Novel backdoor uses OpenAI Assistants API for command and control](/studies/AML.CS0042)
  - [Malware Prototype with Embedded Prompt Injection](/studies/AML.CS0043)
  - [LAMEHUG: Malware Leveraging Dynamic AI-Generated Commands](/studies/AML.CS0044)

- Updated existing case studies

  - [LLM Jacking](/studies/AML.CS0030)

## [5.1.1]() (2025-11-25)

Minor revisions to case studies:
- Added a reference [AIKatz: Attacking LLM Desktop Applications](/studies/AML.CS0036).
- Updated usage of LLM Prompt Injection subtechniques in:
  - [Morris II Worm: RAG-Based Attack](/studies/AML.CS0024)
  - [Data Exfiltration via Agent Tools in Copilot Studio](/studies/AML.CS0037)
  - [Planting Instructions for Delayed Automatic AI Agent Tool Invocation](/studies/AML.CS0038)
  - [Living Off AI: Prompt Injection via Jira Service Management](/studies/AML.CS0039)

## [5.1.0]() (2025-11-06)

This version of ATLAS data contains 1 matrix, 16 tactics, 84 techniques, 56 sub-techniques, 32 mitigations, and 42 case studies.

###### Tactics

- Added a new tactic

  - [Lateral Movement](/techniques/AML.TA0015)

###### Techniques

- Added new techniques

  - [Gather Victim Identity Information](/techniques/AML.T0087)
  - [Generate Deepfakes](/techniques/AML.T0088)
  - [Process Discovery](/techniques/AML.T0089)
  - [OS Credential Dumping](/techniques/AML.T0090)
  - [Use Alternate Authentication Material](/techniques/AML.T0091)
  - [Use Alternate Authentication Material: Application Access Token](/techniques/AML.T0091.000)
  - [Manipulate User LLM Chat History](/techniques/AML.T0092)
  - [Prompt Infiltration via Public-Facing Application](/techniques/AML.T0093)
  - [Delay Execution of LLM Instructions](/techniques/AML.T0094)
  - [Search Open Websites/Domains](/techniques/AML.T0095)

- Updated existing techniques

  - [Active Scanning](/techniques/AML.T0006)
  - [Evade AI Model](/techniques/AML.T0015)
  - [Exfiltration via AI Inference API: Infer Training Data Membership](/techniques/AML.T0024.000)
  - [LLM Prompt Injection: Triggered](/techniques/AML.T0051.002)
  - [AI Agent Tool Invocation](/techniques/AML.T0053)
  - [Data from AI Services](/techniques/AML.T0085)

###### Mitigations

- Added new mitigations
  - [Privileged AI Agent Permissions Configuration](/mitigations/AML.M0026)
  - [Single-User AI Agent Permissions Configuration](/mitigations/AML.M0027)
  - [AI Agent Tools Permissions Configuration](/mitigations/AML.M0028)
  - [Human In-the-Loop for AI Agent Actions](/mitigations/AML.M0029)
  - [Restrict AI Agent Tool Invocation on Untrusted Data](/mitigations/AML.M0030)
  - [Memory Hardening](/mitigations/AML.M0031)

###### Case Studies

- Added new case studies

  - [Live Deepfake Image Injection to Evade Mobile KYC Verification](/studies/AML.CS0033)
  - [ProKYC: Deepfake Tool for Account Fraud Attacks](/studies/AML.CS0034)
  - [Data Exfiltration from Slack AI via Indirect Prompt Injection](/studies/AML.CS0035)
  - [AIKatz: Attacking LLM Desktop Applications](/studies/AML.CS0036)
  - [Data Exfiltration via Agent Tools in Copilot Studio](/studies/AML.CS0037)
  - [Planting Instructions for Delayed Automatic AI Agent Tool Invocation](/studies/AML.CS0038)
  - [Living Off AI: Prompt Injection via Jira Service Management](/studies/AML.CS0039)
  - [Hacking ChatGPT’s Memories with Prompt Injection](/studies/AML.CS0040)
  - [Rules File Backdoor: Supply Chain Attack on AI Coding Assistants](/studies/AML.CS0041)

- Updated existing case studies

  - [Camera Hijack Attack on Facial Recognition System](/studies/AML.CS0004)
  - [Achieving Code Execution in MathGPT via Prompt Injection](/studies/AML.CS0016)
  - [Financial Transaction Hijacking with M365 Copilot as an Insider](/studies/AML.CS0026)
  - [Google Bard Conversation Exfiltration](/studies/AML.CS0029)
  - [ChatGPT Package Hallucination](/studies/AML.CS0022)


## [5.0.1]() (2025-10-15)

Minor language changes and typo fixes.

## [5.0.0]() (2025-09-30)

This version adds the new "Technique Maturity" field to the distributed ATLAS.yaml file. Technique maturity is defined as the level of evidence behind the technique's use:
- Feasible – The technique has been shown to work in a research or academic setting
- Demonstrated – The technique has been shown to be effective in a red team exercise or demonstration on a realistic AI-enabled system
- Realized – The technique has been used by a threat actor in a real-world incident targeting an AI-enabled system

### Techniques

- Added new techniques

  - [AI Agent Context Poisoning](/techniques/AML.T0080)
  - [AI Agent Context Poisoning: Memory](/techniques/AML.T0080.001)
  - [AI Agent Context Poisoning: Thread](/techniques/AML.T0080.001)
  - [Modify AI Agent Configuration](/techniques/AML.T0081)
  - [RAG Credential Harvesting](/techniques/AML.T0082)
  - [Credentials from AI Agent Configuration](/techniques/AML.T0083)
  - [Discover AI Agent Configuration](/techniques/AML.T0084)
  - [Discover AI Agent Configuration: Embedded Knowledge](/techniques/AML.T0084.000)
  - [Discover AI Agent Configuration: Tool Definitions](/techniques/AML.T0084.001)
  - [Discover AI Agent Configuration: Activation Triggers](/techniques/AML.T0084.002)
  - [Data from AI Services](/techniques/AML.T0085)
  - [Data from AI Services: RAG Databases](/techniques/AML.T0085.000)
  - [Data from AI Services: AI Agent Tools](/techniques/AML.T0085.001)
  - [Exfiltration via AI Agent Tool Invocation](/techniques/AML.T0086)
  - [LLM Prompt Injection: Triggered](/techniques/AML.T0051.002)

- Updated existing techniques

  - [AI Agent Tool Invocation](/techniques/AML.T0053)
    - (previously LLM Plugin Compromise)

###### Case Studies

- Added a new case study

  - [Attempted Evasion of ML Phishing Webpage Detection System](/studies/AML.CS0032)

## [4.9.1]() (2025-08-13)

Minor language changes and typo fixes.

## [4.9.0]() (2025-04-22)

The language in TTP names and descriptions has been updated to consistently prefer AI / artificial intelligence over ML / machine learning.

### Tactics

- Added new tactics

  - [Command and Control](/tactics/AML.TA0014)

### Techniques

- Added new techniques

  - [Reverse Shell](/techniques/AML.T0072)
  - [Impersonation](/techniques/AML.T0073)
  - [Masquerading](/techniques/AML.T0074)
  - [Cloud Service Discovery](/techniques/AML.T0075)
  - [Corrupt AI Model](/techniques/AML.T0076)
  - [LLM Response Rendering](/techniques/AML.T0077)
  - [Drive-by Compromise](/techniques/AML.T0078)
  - [Stage Capabilities](/techniques/AML.T0079)
  - [Manipulate AI Model: Embed Malware](/techniques/AML.T0018.002)
  - [AI Supply Chain Compromise: Container Registry](/techniques/AML.T0010.004)
  - [Acquire Infrastructure: Serverless](/techniques/AML.T0008.004)

- Updated existing techniques

  - [Search Open Technical Databases](/techniques/AML.T0000)
    - (previously Search for Victim's Publicly Available Research Materials)
  - [Search Open AI Vulnerability Analysis](/techniques/AML.T0001)
    - (previously Search for Publicly Available Adversarial Vulnerability Analysis)
  - [Manipulate AI Model](/techniques/AML.T0018)
    - (previously Backdoor ML Model)
  - [Manipulate AI Model: Poison AI Model](/techniques/AML.T0018.000)
    - (previously Backdoor ML Model: Poison ML Model)
  - [Manipulate AI Model: Modify AI Model Architecture](/techniques/AML.T0018.001)
    - (previously Backdoor ML Model: Inject Payload)

### Mitigations

- Updated existing mitigations

  - [Vulnerability Scanning](/techniques/AML.M0016)
  - [AI Telemetry Logging](/techniques/AML.M0024)

### Case Studies

- Added new case studies

  - [Organization Confusion on Hugging Face](/studies/AML.CS0027)
  - [AI Model Tampering via Supply Chain Attack](/studies/AML.CS0028)
  - [Google Bard Conversation Exfiltration](/studies/AML.CS0029)
  - [LLM Jacking](/studies/AML.CS0030)
  - [Malicious Models on Hugging Face](/studies/AML.CS0031)

- Updated existing case studies

  - [PoisonGPT](/studies/AML.CS0019)
  - [Indirect Prompt Injection Threats: Bing Chat Data Pirate](/studies/AML.CS0020)
  - [ChatGPT Conversation Exfiltration and Plugin Compromise](/studies/AML.CS0021)

## [4.8.0]() (2025-03-14)

Update to add Zenity case study and associated techniques.

#### Techniques

- Added new techniques

  - [Gather RAG-Indexed Targets](https://atlas.mitre.org/techniques/AML.T0064)
  - [LLM Prompt Crafting](https://atlas.mitre.org/techniques/AML.T0065)
  - [Retrieval Content Crafting](https://atlas.mitre.org/techniques/AML.T0066)
  - [LLM Trusted Output Components Manipulation](https://atlas.mitre.org/techniques/AML.T0067)
  - [LLM Prompt Obfuscation](https://atlas.mitre.org/techniques/AML.T0068)
  - [Discover LLM System Information](https://atlas.mitre.org/techniques/AML.T0069)
  - [RAG Poisoning](https://atlas.mitre.org/techniques/AML.T0070)
  - [False RAG Entry Injection](https://atlas.mitre.org/techniques/AML.T0071)

#### Case Studies

- Added new case studies

  - [Financial Transaction Hijacking with M365 Copilot as an Insider](https://atlas.mitre.org/studies/AML.CS0026)

## [4.7.0]() (2024-10-01)

Generative AI updates

#### Mitigations

- Added new mitigations

  - [Generative AI Guardrails](https://atlas.mitre.org/mitigations/AML.M0020)
  - [Generative AI Guidelines](https://atlas.mitre.org/mitigations/AML.M0021)
  - [Generative AI Model Alignment](https://atlas.mitre.org/mitigations/AML.M0022)
  - [AI Bill of Materials](https://atlas.mitre.org/mitigations/AML.M0023)
  - [AI Telemetry Logging](https://atlas.mitre.org/mitigations/AML.M0024)
  - [Maintain AI Dataset Provenance](https://atlas.mitre.org/mitigations/AML.M0025)

- Refreshed existing mitigations
  - [Limit Public Release of Information](https://atlas.mitre.org/mitigations/AML.M0000)
    - Previously known as "Limit Release of Public Information"

#### Techniques

- Added new techniques

  - [Publish Poisoned Models](https://atlas.mitre.org/techniques/AML.T0058)
  - [Erode Dataset Integrity](https://atlas.mitre.org/techniques/AML.T0059)
  - [User Execution: Malicious Package](https://atlas.mitre.org/techniques/AML.T0011.001)
  - [Publish Hallucinated Entities](https://atlas.mitre.org/techniques/AML.T0060)
  - [LLM Prompt Self-Replication](https://atlas.mitre.org/techniques/AML.T0061)
  - [Discover LLM Hallucinations](https://atlas.mitre.org/techniques/AML.T0062)
  - [Acquire Infrastructure: Domains](https://atlas.mitre.org/techniques/AML.T0008.002)
  - [Acquire Infrastructure: Physical Countermeasures](https://atlas.mitre.org/techniques/AML.T0008.003)
  - [Discover AI Model Outputs](https://atlas.mitre.org/techniques/AML.T0063)

- Refreshed existing techniques
  - [Acquire Infrastructure](https://atlas.mitre.org/techniques/AML.T0008)
  - [ML Supply Chain Compromise: Hardware](https://atlas.mitre.org/techniques/AML.T0010.000)
    - Previously known as "ML Supply Chain Compromise: GPU Hardware"
  - [AI Model Inference API Access](https://atlas.mitre.org/techniques/AML.T0040)
    - Previously known as "ML Model Inference API Access"

#### Case Studies

- Added new case studies

  - [ChatGPT Package Hallucination](https://atlas.mitre.org/studies/AML.CS0022)
  - [ShadowRay](https://atlas.mitre.org/studies/AML.CS0023)
  - [Morris II Worm: RAG-Based Attack](https://atlas.mitre.org/studies/AML.CS0024)
  - [Web-Scale Data Poisoning: Split-View Attack](https://atlas.mitre.org/studies/AML.CS0025)

- Refreshed existing studies
  - [Bypassing Cylance's AI Malware Detection](https://atlas.mitre.org/studies/AML.CS0003)
  - [Attack on Machine Translation Services](https://atlas.mitre.org/studies/AML.CS0005)
  - [ProofPoint Evasion](https://atlas.mitre.org/studies/AML.CS0008)
  - [Face Identification System Evasion via Physical Countermeasures](https://atlas.mitre.org/studies/AML.CS0012)

## [4.6.0]() (2024-07-09)

- Added new fields `created_date` and `modified_date` to all tactic, technique, and mitigation objects
- Updated to use function syntax for internal Jinja-templated Markdown links

## [4.5.2]() (2024-03-11)

Minor fixes

## [4.5.1]() (2024-01-12)

- Added new mitigation
  - [Control Access to ML Models and Data in Production](https://atlas.mitre.org/mitigations/AML.M0019)
- Minor updates to mitigation descriptions and techniques used

## [4.5.0]() (2023-10-25)

Large language models (LLMs)

#### Tactics and techniques

- Added new tactics

  - [Privilege Escalation](https://atlas.mitre.org/tactics/AML.TA0012)
  - [Credential Access](https://atlas.mitre.org/tactics/AML.TA0013)

- Added new techniques
  - [Develop Capabilities](https://atlas.mitre.org/techniques/AML.T0017)
  - [Develop Capabilities: Adversarial ML Attacks](https://atlas.mitre.org/techniques/AML.T0017.000)
    - Previously known as "Develop Adversarial ML Attack Capabilities"
  - [LLM Prompt Injection](https://atlas.mitre.org/techniques/AML.T0051)
  - [LLM Prompt Injection: Direct](https://atlas.mitre.org/techniques/AML.T0051.000)
  - [LLM Prompt Injection: Indirect](https://atlas.mitre.org/techniques/AML.T0051.001)
  - [Phishing](https://atlas.mitre.org/techniques/AML.T0052)
  - [Phishing: Spearphishing via Social Engineering LLM](https://atlas.mitre.org/techniques/AML.T0052.000)
  - [Compromise LLM Plugins](https://atlas.mitre.org/techniques/AML.T0053)
  - [LLM Jailbreak](https://atlas.mitre.org/techniques/AML.T0054)
  - [Unsecured Credentials](https://atlas.mitre.org/techniques/AML.T0055)
  - [LLM Meta Prompt Extraction](https://atlas.mitre.org/techniques/AML.T0056)
  - [LLM Data Leakage](https://atlas.mitre.org/techniques/AML.T0057)
  - [External Harms](https://atlas.mitre.org/techniques/AML.T0048)
    - Previously this technique ID was known as "System Misuse for External Effect"
  - [External Harms: Financial Harm](https://atlas.mitre.org/techniques/AML.T0048.000)
  - [External Harms: Reputational Harm](https://atlas.mitre.org/techniques/AML.T0048.001)
  - [External Harms: Societal Harm](https://atlas.mitre.org/techniques/AML.T0048.002)
  - [External Harms: User Harm](https://atlas.mitre.org/techniques/AML.T0048.003)
  - [External Harms: ML Intellectual Property Theft](https://atlas.mitre.org/techniques/AML.T0048.004)
    - Previously was a top-level technique "ML Intellectual Property Theft", note the ID change

#### Case studies

- Added new case studies

  - [Bypassing ID.me Identity Verification](https://atlas.mitre.org/studies/AML.CS0017)
  - [Arbitrary Code Execution with Google Colab](https://atlas.mitre.org/studies/AML.CS0018)
  - [PoisonGPT](https://atlas.mitre.org/studies/AML.CS0019)
  - [Indirect Prompt Injection Threats: Bing Chat Data Pirate](https://atlas.mitre.org/studies/AML.CS0020)
  - [ChatGPT Plugin Privacy Leak](https://atlas.mitre.org/studies/AML.CS0021)

- Refreshed existing case studies with LLM techniques
  - [Achieving Code Execution in MathGPT via Prompt Injection](https://atlas.mitre.org/studies/AML.CS0016)

## [4.4.2]() (2023-10-12)

- Added ML lifecycle stages and new categories to mitigations.
- Minor updates to tactic and technique descriptions.

## [4.4.1]() (2023-07-18)

Upgrade PyYAML to 6.0.1 to resolve install error - see https://github.com/yaml/pyyaml/issues/601.

## [4.4.0]() (2023-04-12)

Initial mitigations

## [4.3.0]() (2023-02-28)

New case study on prompt injection and adapted new associated techniques from ATT&CK.

#### Tactics and techniques

- Added new techniques
  - [Exploit Public-Facing Application](https://atlas.mitre.org/techniques/AML.T0049)
  - [Command and Scripting Interpreter](https://atlas.mitre.org/techniques/AML.T0050)

#### Case studies

- Added new case study
  - [Achieving Code Execution in MathGPT via Prompt Injection](https://atlas.mitre.org/studies/AML.CS0016)

## [4.2.0]() (2023-01-18)

Denotes existing tactics and techniques adapted from ATT&CK and adds a new case study on a dependency confusion.

#### Tactics and techniques

- Added new technique
  - [Data from Local System](https://atlas.mitre.org/techniques/AML.T0037)
- ATLAS objects that are adapted from ATT&CK are denoted by the additional key `ATT&CK-reference`, ex.
  - ```
    ATT&CK-reference:
      id: T1595
      url: https://attack.mitre.org/techniques/T1595/
    ```

#### Case studies

- Added new case study
  - [Compromised PyTorch Dependency Chain](https://atlas.mitre.org/studies/AML.CS0015)

## [4.1.0]() (2022-10-27)

Refreshed existing case studies

#### Tactics and techniques

- Added a ATLAS technique
  - [System Misuse for External Effect](https://atlas.mitre.org/techniques/AML.T0048)
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
  - The `tactics` and `techniques` keys that was previously at the top-level of this file have been moved into an entry of this `matrices` key
  - Note that case studies remains at the top-level, as they can contain techniques from multiple matrices
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
  - Must start with a prefix of capital letter(s), optionally followed by numbers, then a "." (ex. AML.)
  - Optionally can repeat the above pattern (ex. AML.VER123. )
  - Ending in the expected pattern for the data object (ex. AML.VER123.T1234 )
- Introduced a mitigation object schema for testing `object-type: "mitigation"` data, if exists
- Optional case study references, if exists, expected to be a list

#### Tools

- Updated output YAML generation script to accept arbitrary object types and output them as top-level keys.
  - Ex. `object-type: "mitigation"` produces the top-level key `mitigations:` in `ATLAS.yaml`
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
  - Updated descriptions to be machine learning-specific
  - Changed IDs to ATLAS IDs
- Added ATLAS techniques used in new case studies, adapted from ATT&CK with updated ATLAS IDs and descriptions
  - Data from Information Repositories
  - Establish Accounts
  - Valid Accounts

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
