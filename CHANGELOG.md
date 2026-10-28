## [2026.10]() (2026-10-28)

##### Content v2026.10

This version of ATLAS data contains 1 matrix, 16 tactics, 129 techniques, 92 sub-techniques, 44 mitigations, 77 case studies, 44 entities, and 37 software records.

###### Techniques

- Added new techniques

  - [Develop Capabilities: Malware](/techniques/AML.T0017.003)
  - [Outputs from AI Models](/techniques/AML.T0135)
    - Collection behavior separated out from [Exfiltration via AI Inference API](/techniques/AML.T0024)
  - [Exfiltration via AI User Interface](/techniques/AML.T0136)
  - [Training Data Information from AI Models](/techniques/AML.T0137)
  - [Training Data Information from AI Models: Infer Membership](/techniques/AML.T0137.000)
    - moved from "Exfiltration via AI Inference API: Infer Training Data Membership" (AML.T0024.000)
  - [Training Data Information from AI Models: Infer Properties](/techniques/AML.T0137.001)
  - [Training Data Information from AI Models: Invert AI Model](/techniques/AML.T0137.002)
    - moved from "Exfiltration via AI Inference API: Invert AI Model" (AML.T0024.001)
  - [Training Data Information from AI Models: Extract Memorized Data](/techniques/AML.T0137.003)
  - [Indicator Removal](/techniques/AML.T0138)
  - [Compromise Accounts](/techniques/AML.T0139)
  - [Centralized AI Service Request Routing](/techniques/AML.T0140)
  - [AI Service Request Metadata Sanitization](/techniques/AML.T0141)
  - [Event Triggered Execution](/techniques/AML.T0142)
  - [LLM Prompt Propagation](/techniques/AML.T0143)
  - [Recover AI Model Internals](/techniques/AML.T0144)
  - [Poison AI Agent Learning Environment](/techniques/AML.T0145)
  - [Data from AI Services: Conversation Context and Memory](/techniques/AML.T0085.002)
    - moved from "LLM Data Leakage" (AML.T0057)
  - [Data from AI Services: System Instructions](/techniques/AML.T0085.003)
    - moved from "Extract LLM System Prompt" (AML.T0056)

- Updated existing techniques

  - [Supply Chain Compromise](/techniques/AML.T0010)
    - Previously "AI Supply Chain Compromise"
  - [Supply Chain Compromise: Hardware](/techniques/AML.T0010.000)
  - [Supply Chain Compromise: Software](/techniques/AML.T0010.001)
    - Previously "AI Supply Chain Compromise: AI Software"
  - [Supply Chain Compromise: Data Repository](/techniques/AML.T0010.002)
    - Previously "AI Supply Chain Compromise: Data"
  - [Supply Chain Compromise: Model Repository](/techniques/AML.T0010.003)
    - Previously "AI Supply Chain Compromise: Model"
  - [Replicate AI Model Behavior](/techniques/AML.T0005)
    - Previously "Create AI Proxy Model"
  - [Replicate AI Model Behavior: Replicate Behavior from Gathered AI Artifacts](/techniques/AML.T0005.000)
    - Previously "Create Proxy AI Model: Train Proxy via Gathered AI Artifacts"
  - [Replicate AI Model Behavior: Replicate Behavior from Model Outputs](/techniques/AML.T0005.001)
    - Previously "Create Proxy AI Model: Train Proxy via Replication"
  - [Replicate AI Model Behavior: Adapt Existing Model to Replicate Behavior](/techniques/AML.T0005.002)
    - Previously "Create Proxy AI Model: Use Pre-Trained Model"
  - [Data from AI Services: RAG Databases](/techniques/AML.T0085.000)
  - [Data from AI Services: AI Agent Tools](/techniques/AML.T0085.001)
  - [Data from AI Services](/techniques/AML.T0085)
  - [Acquire Infrastructure: AI Service Proxies](/techniques/AML.T0008.005)
  - [Establish Accounts](/techniques/AML.T0021)
  - [Exfiltration via AI Inference API](/techniques/AML.T0024)
  - [AI Intellectual Property Theft](/techniques/AML.T0048.004)
  - [Phishing: Spearphishing via Social Engineering LLM](/techniques/AML.T0052.000)
  - [AI Agent Tool Invocation](/techniques/AML.T0053)
  - [LLM Prompt Self-Replication](/techniques/AML.T0061)
  - [Discover AI Model Outputs](/techniques/AML.T0063)
  - [LLM Prompt Crafting](/techniques/AML.T0065)
  - [Impersonation](/techniques/AML.T0073)
  - [Crafted AI Assistant Links](/techniques/AML.T0131)

###### Mitigations

- Added new mitigations

  - [Adaptive AI Response Degradation](/mitigations/AML.M0040)
  - [Privacy-Preserving AI Training and Inference](/mitigations/AML.M0041)
  - [Threat Intelligence Program](/mitigations/AML.M0042)
  - [AI Agent External Resource Lifecycle Management](/mitigations/AML.M0043)

- Updated existing mitigations

  - [Sanitize Training Data](/mitigations/AML.M0007)
  - [Validate AI Model](/mitigations/AML.M0008)
  - [Verify AI Artifacts](/mitigations/AML.M0014)
  - [Generative AI Guardrails](/mitigations/AML.M0020)
  - [Generative AI Model Alignment](/mitigations/AML.M0022)
  - [Manage Service AI Agent Access](/mitigations/AML.M0026)
    - Previously "Privileged AI Agent Permissions Configuration"
  - [Manage User-Delegated AI Agent Access](/mitigations/AML.M0027)
    - Previously "Single-User AI Agent Permissions Configuration"
  - [Enforce Access Controls for AI Agent Tools](/mitigations/AML.M0028)
    - Previously "AI Agent Tools Permissions Configuration"
  - [Maintain an AI Bill of Materials](/mitigations/AML.M0023)
    - Previously "AI Bill of Materials"
  - [AI Telemetry Logging and Monitoring](/mitigations/AML.M0024)
    - Previously "AI Telemetry Logging"
  - [AI Agent Authority Expansion Controls](/mitigations/AML.M0037)
  - [AI Agent Scope Drift Detection](/mitigations/AML.M0038)
    - Updated mitigation-to-technique relationships
      - [Limit Public Release of Information](/mitigations/AML.M0000)
      - [Limit Model Artifact Release](/mitigations/AML.M0001)
      - [Predictive AI Output Obfuscation](/mitigations/AML.M0002)
      - [Limit AI Service Query Volume and Rate](/mitigations/AML.M0004)
      - [Control Access to AI Models and Data at Rest](/mitigations/AML.M0005)
      - [Predictive AI Ensembles](/mitigations/AML.M0006)
      - [Restrict Library Loading](/mitigations/AML.M0011)
      - [Code Signing](/mitigations/AML.M0013)
      - [Vulnerability Scanning](/mitigations/AML.M0016)
      - [Generative AI Guidelines](/mitigations/AML.M0021)
      - [Maintain AI Dataset Provenance](/mitigations/AML.M0025)
      - [Human In-the-Loop for AI Agent Actions](/mitigations/AML.M0029)
      - [Restrict AI Agent Tool Invocation on Untrusted Data](/mitigations/AML.M0030)
      - [Segmentation of AI Agent Components](/mitigations/AML.M0032)
      - [Input and Output Validation for AI Agent Components](/mitigations/AML.M0033)
      - [AI Red Team](/mitigations/AML.M0035)
      - [Limit AI Workload Resource Consumption](/mitigations/AML.M0036)
      - [AI Honeypots](/mitigations/AML.M0039)

###### Case Studies

- Added new case studies

  - [Autonomous Claude Agents Compromise Three Real Organizations During Cyber Evaluations](/studies/AML.CS0073)
  - [AISI Evaluation Agents Conduct Unsanctioned Real-World Cyber Activity](/studies/AML.CS0074)
  - [Model Distillation Campaigns Targeting Google AI Services](/studies/AML.CS0075)
  - [China-Based Artificial Intelligence Companies Conducting Industrial-Scale Distillation Campaigns Against U.S. AI Companies](/studies/AML.CS0076)

- Updated existing case studies

  - Added entity and software relationships for all applicable case studies
  - [Model Distillation Campaigns Targeting Anthropic Claude](/studies/AML.CS0056)
  - [GTG-1002 Claude Code Espionage Campaign](/studies/AML.CS0069)
  - [LLMjacking: Stolen Cloud Credentials Used to Access Cloud LLM Services](/studies/AML.CS0030)
    - Previously "LLM Jacking"
  - Updated attack chains
    - [Attack on Machine Translation Services](/studies/AML.CS0005)
    - [ProofPoint Evasion](/studies/AML.CS0008)
    - [Confusing Antimalware Neural Networks](/studies/AML.CS0014)
    - [Achieving Code Execution in MathGPT via Prompt Injection](/studies/AML.CS0016)
    - [Arbitrary Code Execution with Google Colab](/studies/AML.CS0018)
    - [ShadowRay: Hijacking Exposed Ray Clusters](/studies/AML.CS0023)
    - [AIKatz: Attacking LLM Desktop Applications](/studies/AML.CS0036)
    - [Data Exfiltration via Agent Tools in Copilot Studio](/studies/AML.CS0037)
    - [Organization Confusion on Hugging Face](/studies/AML.CS0027)
    - [AI Model Tampering via Supply Chain Attack](/studies/AML.CS0028)
    - [Data Exfiltration via Remote Poisoned MCP Tool](/studies/AML.CS0054)
    - [Prompt-Based Attacks Against Gemini via Calendar Invitations](/studies/AML.CS0063)
    - [Morris II Worm: RAG-Based Attack](/studies/AML.CS0024)
    - [Rules File Backdoor: Supply Chain Attack on AI Coding Assistants](/studies/AML.CS0041)
    - [ZombieAgent: Data Exfiltration Attack on ChatGPT](/studies/AML.CS0066)
  - Added AI Incident Database references
    - [LAMEHUG: Malware Leveraging Dynamic AI-Generated Commands](/studies/AML.CS0044)
    - [Code to Deploy Destructive AI Agent Discovered in Amazon Q VS Code Extension](/studies/AML.CS0047)
    - [Storm-2139 Azure OpenAI Guardrail Bypass](/studies/AML.CS0057)
    - [Model Distillation Campaigns Targeting Anthropic Claude](/studies/AML.CS0056)
    - [Autonomous OpenAI Evaluation Agents Compromise Hugging Face Infrastructure](/studies/AML.CS0068)
    - [GTG-1002 Claude Code Espionage Campaign](/studies/AML.CS0069)
    - [Multi-Agent Framework Compromises Taiwanese Government Systems](/studies/AML.CS0071)
  - Updated date to range
    - [Tay Poisoning](/studies/AML.CS0009)
    - [Compromised PyTorch Dependency Chain](/studies/AML.CS0015)
    - [Bypassing ID.me Identity Verification](/studies/AML.CS0017)
    - [Web-Scale Data Poisoning: Split-View Attack](/studies/AML.CS0025)
    - [Code to Deploy Destructive AI Agent Discovered in Amazon Q VS Code Extension](/studies/AML.CS0047)
    - [Poisoned Postmark MCP Server Email Exfiltration](/studies/AML.CS0053)
    - [Storm-2139 Azure OpenAI Guardrail Bypass](/studies/AML.CS0057)
    - [Autonomous OpenAI Evaluation Agents Compromise Hugging Face Infrastructure](/studies/AML.CS0068)
    - [Multi-Agent Framework Compromises Taiwanese Government Systems](/studies/AML.CS0071)
    - [Autonomous Claude Agents Compromise Three Real Organizations During Cyber Evaluations](/studies/AML.CS0073)

###### Entities

- Added new entities

  - [MITRE AI Red Team](/entities/AML.E0000)
  - [Microsoft AI Red Team](/entities/AML.E0001)
  - [Silent Break Security](/entities/AML.E0002)
  - [spiderSilk](/entities/AML.E0003)
  - [Berkeley Artificial Intelligence Research](/entities/AML.E0004)
  - [Skylight Cyber](/entities/AML.E0005)
  - [Mithril Security](/entities/AML.E0006)
  - [Embrace the Red](/entities/AML.E0007)
  - [Tenable](/entities/AML.E0008)
  - [Lasso Security](/entities/AML.E0009)
  - [Zenity](/entities/AML.E0010)
  - [Trend Micro](/entities/AML.E0011)
  - [iProov Red Team](/entities/AML.E0012)
  - [ProKYC](/entities/AML.E0013)
  - [PromptArmor](/entities/AML.E0014)
  - [Lumia Security](/entities/AML.E0015)
  - [Cato Networks](/entities/AML.E0016)
  - [Pillar Security](/entities/AML.E0017)
  - [APT28](/entities/AML.E0018)
  - [Backslash Security Research Team](/entities/AML.E0019)
  - [HiddenLayer](/entities/AML.E0020)
  - [lkmanka58](/entities/AML.E0021)
  - [depthfirst](/entities/AML.E0022)
  - [Snyk](/entities/AML.E0023)
  - [DeepSeek](/entities/AML.E0024)
  - [Moonshot AI](/entities/AML.E0025)
  - [MiniMax](/entities/AML.E0026)
  - [Storm-2139](/entities/AML.E0027)
  - [Skyld](/entities/AML.E0028)
  - [Cybernews Investigation Team](/entities/AML.E0029)
  - [Check Point Research](/entities/AML.E0030)
  - [Microsoft Defender Security Research Team](/entities/AML.E0031)
  - [SafeBreach Labs](/entities/AML.E0032)
  - [Fujitsu](/entities/AML.E0033)
  - [Unit 42](/entities/AML.E0034)
  - [Radware](/entities/AML.E0035)
  - [OpenAI](/entities/AML.E0036)
  - [GTG-1002](/entities/AML.E0037)
  - [knaithe](/entities/AML.E0038)
  - [Anthropic](/entities/AML.E0039)
  - [Alibaba Group](/entities/AML.E0040)
  - [StepFun](/entities/AML.E0041)
  - [Z.AI](/entities/AML.E0042)
  - [UNC5673](/entities/AML.E0043)

###### Software

- Added new software

  - [Proof Pudding](/software/AML.S0000)
  - [metame](/software/AML.S0001)
  - [Apktool](/software/AML.S0002)
  - [DeepPayload](/software/AML.S0003)
  - [torchtriton](/software/AML.S0004)
  - [ROME](/software/AML.S0005)
  - [EasyEdit](/software/AML.S0006)
  - [huggingface-cli](/software/AML.S0007)
  - [keychecker](/software/AML.S0008)
  - [OAI Reverse Proxy](/software/AML.S0009)
  - [Sliver](/software/AML.S0010)
  - [OBS Studio](/software/AML.S0011)
  - [ProKYC](/software/AML.S0012)
  - [Swapface](/software/AML.S0013)
  - [Virtual Camera: Live Assist](/software/AML.S0014)
  - [LAMEHUG](/software/AML.S0015)
  - [SesameOp](/software/AML.S0016)
  - [HONESTCUE](/software/AML.S0017)
  - [Xanthorox](/software/AML.S0018)
  - [postmark-mcp](/software/AML.S0019)
  - [de3u](/software/AML.S0020)
  - [Frida](/software/AML.S0021)
  - [Claude Code](/software/AML.S0022)
  - [Codex](/software/AML.S0023)
  - [G0DM0D3](/software/AML.S0024)
  - [Hermes Agent](/software/AML.S0025)
  - [OpenClaw](/software/AML.S0026)
  - [Tesseract OCR](/software/AML.S0027)
  - [AI Share URL Creator](/software/AML.S0028)
  - [CiteMET](/software/AML.S0029)
  - [Shodan](/software/AML.S0030)
  - [FOFA](/software/AML.S0031)
  - [Claude Relay Service](/software/AML.S0032)
  - [L1B3RT4S](/software/AML.S0033)
  - [DAN (Do Anything Now)](/software/AML.S0034)
  - [FRUITSHELL](/software/AML.S0035)
  - [CLIProxyAPI](/software/AML.S0036)

##### Data Format v6.1.0

- Added first-class Entity and Software objects to the ATLAS YAML format
  - added top-level `entities` and `software` dictionaries with versioned identities, references, and creation/modification dates
  - Entities use `AML.E####` IDs and an `entity-type` of Activity Cluster, Organization, Team, or Individual
  - added `associated-entities` names with optional descriptions and optional ATT&CK references
  - Software uses `AML.S####` IDs and a `software-type` of Malware or Tool
  - added software aliases, optional ATT&CK references, and `software-categories`: program, library, model, service, ai-agent, ai-agent-framework, ai-agent-integration, and prompt-package
- Added relationships for attribution, reporting, and software use
  - Case Study → Entity: `attributed-to`
  - Incident Case Study → Entity: optional `reported-by`, alongside the existing free-text `reporter`
  - Entity → Technique and Entity → Software: `uses`
  - Case Study → Software: `uses`, independent of actor attribution
  - Software → Technique: `implements`
  - attribution and entity-to-technique relationships require an `activity-purpose`: Adversarial Operation, Security Evaluation, or Unintended Consequence
  - relationships support optional descriptions; activity purpose describes an activity rather than the entity's identity
- Updated case-study metadata
  - made free-text `actor` optional to support structured entity attribution
  - replaced `date` and `date-granularity` with `start-date`, `start-date-granularity`, and optional `end-date` and `end-date-granularity`
  - dates support Year, Month, or Day granularity; an omitted end date represents an ongoing period
- Updated case-study attack chains to support directed graphs
  - added `step-id` and `leads-to` metadata to technique-use relationships, supporting branching paths and repeated use of a technique
- Made technique `maturity` an explicitly provided and stored field with Feasible, Demonstrated, and Realized values

##### Data Tools

- Added API endpoints, schema validation, database models, and migrations for entities, software, and their relationships
- Updated YAML import/export and database population for format 6.1.0, including compatibility handling for legacy case-study dates
- Updated version copying and deletion to preserve or remove entity/software records and relationships with their data version
- Updated Excel generation to include entities, software, attribution, reporting, and software-use relationships
- Updated STIX generation to include entity/software objects and their supported relationships, including case-study software use
  - reporting relationships, free-text reporter information, and activity-purpose metadata remain outside the STIX export
- Added Attack Flow generation for case-study attack-chain graphs and release artifacts
- Improved sub-technique relationship handling and validation
- Updated release workflows to validate releases, check out the requested release tag, and pin ATT&CK data used for STIX generation
- Updated the pinned Enterprise ATT&CK dataset used for combined STIX exports from v19.2 to v20.0

## [2026.09]() (2026-09-14)

##### Content v2026.09

This version of ATLAS data contains 1 matrix, 16 tactics, 120 techniques, 88 sub-techniques, 40 mitigations, and 73 case studies.

###### Techniques

- Added new techniques

  - [Triggers in Multimodal Inputs](/techniques/AML.T0129)
  - [AI Agent Response Biasing](/techniques/AML.T0130)
  - [Crafted AI Assistant Links](/techniques/AML.T0131)
  - [Misconfigured or Publicly Exposed AI Services](/techniques/AML.T0132)
  - [Discover AI Agent Runtime Capabilities](/techniques/AML.T0133)
  - [AI Targeted Cloaking](/techniques/AML.T0134)
  - [Search Open Technical Databases: Scan Databases](/techniques/AML.T0000.003)
  - [Active Scanning: Enumerate Hosted AI Resources](/techniques/AML.T0006.000)
  - [Active Scanning: Query Platform Metadata APIs](/techniques/AML.T0006.001)
  - [Active Scanning: Scan for Exposed AI Infrastructure](/techniques/AML.T0006.002)
  - [Active Scanning: Probe AI Agent Trigger Channels](/techniques/AML.T0006.003)

- Updated existing techniques

  - [Search Open Technical Databases](/techniques/AML.T0000)
  - [Search Open Website/Domains](/techniques/AML.T0095)
  - [Active Scanning](/techniques/AML.T0006)
  - [LLM Prompt Obfuscation](/techniques/AML.T0068)
  - [LLM Prompt Injection: Indirect](/techniques/AML.T0051.001)
  - [LLM Jailbreak](/techniques/AML.T0054)
  - [LLM Response Rendering](/techniques/AML.T0077)
  - [AI Agent Clickbait](/techniques/AML.T0100)

###### Mitigations

- Added new mitigations

  - [AI Honeypots](/mitigations/AML.M0039)

- Updated existing mitigations

  - [Generative AI Guardrails](/mitigations/AML.M0020)

###### Case Studies

- Added new case studies

  - [AI Recommendation Poisoning via Crafted AI Assistant Links](/studies/AML.CS0072)

- Updated existing case studies

  - [ShadowRay: Hijacking Exposed Ray Clusters](/studies/AML.CS0023)
  - [Data Exfiltration via Agent Tools in Copilot Studio](/studies/AML.CS0037)
  - [Exposed ClawdBot Control Interfaces Leads to Credential Access and Execution](/studies/AML.CS0048)
  - [Threat Actor Uses a DeepSeek-Powered Hermes Agent in Langflow and n8n Exploitation Attempts](/studies/AML.CS0070)


## [2026.08]() (2026-08-31)

##### Content v2026.08

This version of ATLAS data contains 1 matrix, 16 tactics, 114 techniques, 83 sub-techniques, 39 mitigations, and 72 case studies.

ATLAS is a globally accessible, living knowledge base of adversary tactics and techniques involving AI, including attacks against AI-enabled systems, abuse or manipulation of AI capabilities, and harmful autonomous behavior materially enabled by AI. ATLAS is based on empirical evidence from observations of real-world attacks as well as realistic demonstrations from AI red teams and security groups.

###### Matrices

- Updated existing matrices

  - [ATLAS Matrix](/matrices/ATLAS-matrix)

###### Tactics

- Updated existing tactics

  - [AI Attack Adaptation](/tactics/AML.TA0001)
    - Previously "AI Attack Staging"

###### Techniques

- Added new techniques

  - [Autonomous Reconnaissance](/techniques/AML.T0116)
  - [Autonomous Attack-Path Adaptation](/techniques/AML.T0117)
  - [Autonomous AI Agent Communication](/techniques/AML.T0118)
  - [Autonomous AI Agent Communication: Communication via Shared Artifacts](/techniques/AML.T0118.000)
  - [Autonomous AI Agent Communication: Direct Agent Communication](/techniques/AML.T0118.001)
  - [Exploit Automated Artifact Processing Pipeline](/techniques/AML.T0119)
  - [AI Artifact Repository](/techniques/AML.T0120)
  - [AI Agent Environment Reconstruction](/techniques/AML.T0121)
  - [Exploitation of Remote Services](/techniques/AML.T0122)
  - [Obfuscated Files or Information](/techniques/AML.T0123)
  - [Autonomous Attack Orchestration](/techniques/AML.T0124)
  - [Create Account](/techniques/AML.T0125)
  - [Automated Collection](/techniques/AML.T0126)
  - [Data Staged](/techniques/AML.T0127)
  - [Compromise Infrastructure](/techniques/AML.T0128)
  - [Develop Capabilities: Autonomous Exploit Development](/techniques/AML.T0017.001)
  - [Develop Capabilities: AI Agent Tools](/techniques/AML.T0017.002)
  - [Obtain Capabilities: AI Agent Tools](/techniques/AML.T0016.004)

- Updated existing techniques

  - [Enterprise Resource Discovery](/techniques/AML.T0075)
    - Generalized from "Cloud Service Discoery"
  - [Enterprise Environment Discovery](/techniques/AML.T0089)
    - Generalized from "Process Discovery"
  - [Cyber Communication Channel](/techniques/AML.T0072)
    - Generalized from "Reverse Shell"
  - [Develop Capabilities](/techniques/AML.T0017)
  - [LLM Prompt Crafting](/techniques/AML.T0065)
  - [Retrieval Content Crafting](/techniques/AML.T0066)

###### Mitigations

- Added new mitigations

  - [AI Agent Authority Expansion Controls](/mitigations/AML.M0037)
  - [AI Agent Scope Drift Detection](/mitigations/AML.M0038)

- Updated existing mitigations

  - [Generative AI Model Alignment](/mitigations/AML.M0022)
  - [Segmentation of AI Agent Components](/mitigations/AML.M0032)
  - [Vulnerability Scanning](/mitigations/AML.M0016)
  - [AI Red Team](/mitigations/AML.M0035)

###### Case Studies

- Added new case studies

  - [Autonomous OpenAI Evaluation Agents Compromise Hugging Face Infrastructure](/studies/AML.CS0068)
  - [GTG-1002 Claude Code Espionage Campaign](/studies/AML.CS0069)
  - [Threat Actor Uses a DeepSeek-Powered Hermes Agent in Langflow and n8n Exploitation Attempts](/studies/AML.CS0070)
  - [Multi-Agent Framework Compromises Taiwanese Government Systems](/studies/AML.CS0071)


## [2026.07]() (2026-07-31)

##### Content v2026.07

This version of ATLAS data contains 1 matrix, 16 tactics, 101 techniques, 77 sub-techniques, 37 mitigations, and 68 case studies.

###### Techniques

- Added new techniques

  - [Publish Poisoned AI Artifacts](/techniques/AML.T0115)
  - [Manipulate AI Model: Modify Prompt Construction Logic](/techniques/AML.T0018.003)
  - [AI Agent Tool Poisoning: Definition and Instructions](/techniques/AML.T0110.000)
  - [AI Agent Tool Poisoning: Implementation](/techniques/AML.T0110.001)
  - [AI Agent Tool Poisoning: Runtime Response](/techniques/AML.T0110.002)

- Updated existing techniques

  - [Publish Poisoned AI Artifacts: Datasets](/techniques/AML.T0115.000)
    - Previously "Publish Poisoned Datasets" (AML.T0019)
  - [Publish Poisoned AI Artifacts: Models](/techniques/AML.T0115.001)
    - Previously "Publish Poisoned Models" (AML.T0058)
  - [Publish Poisoned AI Artifacts: AI Agent Tools](/techniques/AML.T0115.002)
    - Previously "Publish Poisoned AI Agent Tool" (AML.T0104)
  - [Training Data Poisoning](/techniques/AML.T0020)
    - Previously called Poison Training Data
  - [Masquerading](/techniques/AML.T0074)
  - [AI Agent Tool Poisoning](/techniques/AML.T0110)
  - [AI Agent Tool Invocation](/techniques/AML.T0053)
  - [AI Supply Chain Compromise: AI Agent Tool](/techniques/AML.T0010.005)
  - [User Execution: Unsafe AI Artifacts](/techniques/AML.T0011.000)
  - [User Execution: Poisoned AI Agent Tool](/techniques/AML.T0011.002)
  - [Acquire Public AI Artifacts: AI Agent Configuration](/techniques/AML.T0002.002)
  - [AI Agent Tool Data Poisoning](/techniques/AML.T0099)
  - [Manipulate AI Model](/techniques/AML.T0018)

###### Mitigations

- Added new mitigations

  - [AI Red Team](/mitigations/AML.M0035)
  - [Limit AI Workload Resource Consumption](/mitigations/AML.M0036)

- Updated existing mitigations

  - [Memory Hardening](/mitigations/AML.M0031)
  - [Generative AI Model Alignment](/mitigations/AML.M0022)
  - [Passive AI Output Obfuscation](/mitigations/AML.M0002)
    - Previously called "Passive AI Output Obfuscation"
  - [Predictive AI Model Hardening](/mitigations/AML.M0003)
    - Previously called "Model Hardening"
  - [Predictive AI Ensembles](/mitigations/AML.M0006)
    - Previously called "Use Ensemble Methods"
  - [Predictive AI Multi-Sensor Fusion](/mitigations/AML.M0009)
    - Previously called "Use Multi-Modal Sensors"
  - [Predictive AI Input Restoration](/mitigations/AML.M0010)
    - Previously called "Input Restoration"
  - [Predictive AI Adversarial Input Detection](/mitigations/AML.M0015)
    - Previously called "Adversarial Input Detection"
  - [Limit AI Service Query Volume and Rate](/mitigations/AML.M0004)
    - Previously called "Restrict Number of AI Model Queries"
  - [Limit Public Release of Information](/mitigations/AML.M0000)
  - [Limit Model Artifact Release](/mitigations/AML.M0001)
  - [Control Access to AI Models and Data at Rest](/mitigations/AML.M0005)
  - [Restrict Library Loading](/mitigations/AML.M0011)
  - [Control Access to AI Models and Data in Production](/mitigations/AML.M0019)
  - [Generative AI Guardrails](/mitigations/AML.M0020)
  - [Generative AI Guidelines](/mitigations/AML.M0021)
  - [Maintain AI Dataset Provenance](/mitigations/AML.M0025)
  - [Segmentation of AI Agent Components](/mitigations/AML.M0032)

###### Case Studies

- Added new case studies

  - [Prompt-Based Attacks Against Gemini via Calendar Invitations](/studies/AML.CS0063)
  - [Poisoned GGUF Templates: Inference-Time Supply Chain Attack](/studies/AML.CS0064)
  - [Model Namespace Reuse Supply Chain Attack](/studies/AML.CS0065)
  - [ZombieAgent: Data Exfiltration Attack on ChatGPT](/studies/AML.CS0066)
  - [Claude Code GitHub Action Secret Exposure](/studies/AML.CS0067)

- Updated existing case studies

  - [Web-Scale Data Poisoning: Split-View Attack](/studies/AML.CS0025)
  - [ShadowRay: Hijacking Exposed Ray Clusters](/studies/AML.CS0023)
    - Previously called "ShadowRay"
  - [Supply Chain Compromise via Poisoned ClawdBot Skill](/studies/AML.CS0049)
  - [Poisoned Postmark MCP Server Email Exfiltration](/studies/AML.CS0053)
  - [Data Exfiltration via Remote Poisoned MCP Tool](/studies/AML.CS0054)

##### Data Tools

- Added stix-atlas-attack-enterprise.json to release artifacts
- Updated navigator layer generation

## [2026.06]() (2026-06-30)

##### Content v2026.06

###### Techniques

- Added new techniques

  - [Steal Web Session Cookie](/techniques/AML.T0113)
  - [Use Alternate Authentication Material: Web Session Cookie](/techniques/AML.T0091.001)
  - [AI Service Web Interface](/techniques/AML.T0114)

- Updated existing techniques

  - [LLM Jailbreak](/techniques/AML.T0054)

###### Mitigations

- Updated existing mitigations

  - [Generative AI Guardrails](/mitigations/AML.M0020)
  - [Generative AI Guidelines](/mitigations/AML.M0021)
  - [AI Telemetry Logging](/mitigations/AML.M0024)

###### Case Studies

- Added new case studies

  - [Storm-2139 Azure OpenAI Guardrail Bypass](/studies/AML.CS0057)
  - [Google Photos AI Model Extraction](/studies/AML.CS0058)
  - [EchoLeak: Zero-Click Prompt Injection Targeting M365 Copilot for Data Exfiltration](/studies/AML.CS0059)
  - [Cross-Site Scripting via Prompt Manipulation in Lenovo’s AI Chatbot](/studies/AML.CS0060)
  - [AI in the Middle: Web-Based AI Services as C2 Relays](/studies/AML.CS0061)
  - [RCE Vulnerability in Semantic Kernel Search Plugin](/studies/AML.CS0062)


## [2026.05]() (2026-05-27)

Starting with this release, there is a split in versioning between the ATLAS Knowledge Base content and the ATLAS Data Format. Monthly ATLAS content releases will follow a YYYY.MM.N versioning scheme with the version stored in the Collection object. ATLAS data format changes will follow semantic versioning. Previously, changes to either content or format were conflated in a single SemVer version.

##### Content v2026.05

- All techniques are updated to include one or more platforms (Predictive AI, Generative AI, Agentic AI, Enterprise).

##### Format v6.0.0

- Introduced a new ATLAS YAML format (v6.0.0)
  - stronger consistency, normalized object modeling, and first-class relationship representation
  - added platforms field to techniques
- Added full validation and data management tooling
  - Pydantic schemas for strict schema validation
  - SQLAlchemy ORM models for persistent versioned content management
  - FastAPI REST API for managing and updating ATLAS data
- Removed the old workflow for constructing ATLAS.yaml
- Added/updated downstream generation scripts for STIX, Excel, and Navigator outputs
  - centralized all downstream scripts to the atlas-data repository
- Added a test suite for the API
- Migrated and preserved historical ATLAS releases:
  - historical content retained under dist/legacy/
  - historical releases migrated into the v6 structure (dist/v6/)
  - release/version mapping tracked in manifest
  - deprecated ATLAS.yaml

###### ATLAS v6 data model

The v6 format introduces substantial structural improvements:
- Added new field to techniques that denotes the platform(s) the adversary is operating in
- Standardized top-level export model around:
  - collection, matrix
  - keyed maps for tactics, techniques, mitigations, case-studies.
  - centralized relationships map for easier downstream consumption.
- Enforced consistency in object typing and identity:
  - common field names across object types.
  - computed UUID behavior tied to stable IDs.
  - canonical ID patterns per object type.
  - strict object-type enums.
- Elevated relationships to first-class objects with typed semantics:
  - sequences, achieves, specializes, mitigates, employs.
  - support for relationship metadata like position, tactic, step-id, leads-to, and descriptions.
- Cleaned and normalized reference handling and serialization behavior.
- Improved date handling/constraints and enum ordering consistency.

###### API, database, and validation
- Added FastAPI app entrypoint and route structure for:
  - version lifecycle management.
  - version-scoped CRUD across collection, matrix, tactics, techniques, mitigations, and case studies.
  - YAML export endpoint for a selected version.
- Added SQLAlchemy model layer with:
  - version-aware object storage.
  - relationship table and integrity constraints.
  - derived ORM properties for graph-style access patterns.
- Added script to populate DB from ATLAS YAML v6.
- Normalized export behavior for deterministic output.

###### Tools for downstream asset generation
- Updated STIX generation with maturity filtering and improved compatibility options.
- Updated Navigator layer generation for matrix and case-study visualizations.
- Updated Excel generation workflow for generating workbook artifacts.
- Consolidated scripts into tools/ directory (from other repositories).
- Added CI/release workflows for publishing YAML/STIX/Navigator/Excel artifacts.

###### Testing
- Added integration tests for API behavior and data round-tripping.
- Updated CI workflows and validation checks.
- Refactored test structure to align with the new architecture.


## [5.6.1]() (2026-05-05)

Minor fixes to contribution schemas.

## [5.6.0]() (2026-04-30)

###### Techniques

- Added new techniques

  - [Acquire Public AI Artifacts: AI Agent Configuration](/techniques/AML.T0002.002)
  - [Search Open Websites/Domains: Code Repositories](/techniques/AML.T0095.000)
  - [Phishing: Deepfake-Assisted Phishing](/techniques/AML.T0052.001)


- Updated existing techniques

  - [Phishing](/techniques/AML.T0052)
  - [LLM Jailbreak](/techniques/AML.T0054)

###### Mitigations

- Updated existing mitigations

  - [User Training](/mitigations/AML.M0018)
  - [Deepfake Detection](/mitigations/AML.M0034)

###### Case Studies

- Updated existing case studies

  - [OpenClaw Command & Control via Prompt Injection](/studies/AML.CS0051)

## [5.5.0]() (2026-03-30)

###### Techniques

- Added new techniques

  - [AI Agent Tool Poisoning](/techniques/AML.T0110)
  - [AI Supply Chain Rug Pull](/techniques/AML.T0109)
  - [AI Agent Tool Poisoning](/techniques/AML.T0110)
  - [AI Supply Chain Reputation Inflation](/techniques/AML.T0111)
  - [Machine Compromise](/techniques/AML.T0112)
  - [Machine Compromise: Local AI Agent](/techniques/AML.T0112.000)
  - [Machine Compromise: AI Artifacts](/techniques/AML.T0112.001)
  - [Cost Harvesting: Excessive Queries](/techniques/AML.T0034.000)
  - [Cost Harvesting: Resource-Intensive Queries](/techniques/AML.T0034.001)
  - [Cost Harvesting: Agentic Resource Consumption](/techniques/AML.T0034.002)
  - [Discover AI Agent Configuration: Call Chains](/techniques/AML.T0084.003)
  - [Acquire Infrastructure: AI Service Proxies](/techniques/AML.T0008.005)

- Updated existing techniques

  - [Cost Harvesting](/techniques/AML.T0034)
  - [Exfiltration via AI Agent Tool Invocation](/techniques/AML.T0086)
  - [Publish Poisoned AI Agent Tool](/techniques/AML.T0104)

###### Mitigations

- Updated existing mitigations

  - [Code Signing](/mitigations/AML.M0013)
  - [AI Telemetry Logging](/mitigations/AML.M0024)
  - [Segmentation of AI Agent Components](/mitigations/AML.M0032)

###### Case Studies

- Added new case studies

  - [LLMSmith: RCE Vulnerabilities in LLM-Integrated Applications](/studies/AML.CS0052)
  - [Poisoned Postmark MCP Server Email Exfiltration](/studies/AML.CS0053)
  - [Data Exfiltration via Remote Poisoned MCP Tool](/studies/AML.CS0054)
  - [AI ClickFix: Hijacking Computer-Use Agents Using ClickFix](/studies/AML.CS0055)
  - [Model Distillation Campaigns Targeting Anthropic Claude](/studies/AML.CS0056)


- Updated existing case studies

  - [Supply Chain Compromise via Poisoned ClawdBot Skill](/studies/AML.CS0049)

## [5.4.0]() (2026-02-05)

###### Techniques

- Added new techniques

  - [Publish Poisoned AI Agent Tool](/techniques/AML.T0104)
  - [Escape to Host](/techniques/AML.T0105)
  - [Exploitation for Credential Access](/techniques/AML.T0106)
  - [Exploitation for Defense Evasion](/techniques/AML.T0107)
  - [AI Agent](/techniques/AML.T0108)
  - [User Execution: Poisoned AI Agent Tool](/techniques/AML.T0011.002)
  - [User Execution: Malicious Link](/techniques/AML.T0011.003)

- Updated existing techniques

  - [Modify AI Agent Configuration](/techniques/AML.T0081)

###### Case Studies

- Added new case studies

  - [Exposed ClawdBot Control Interfaces Leads to Credential Access and Execution](/studies/AML.CS0048)
  - [Supply Chain Compromise via Poisoned ClawdBot Skill](/studies/AML.CS0049)
  - [OpenClaw 1-Click Remote Code Execution](/studies/AML.CS0050)
  - [OpenClaw Command & Control via Prompt Injection](/studies/AML.CS0051)

## [5.3.0]() (2026-01-30)

###### Techniques

- Added new techniques

  - [Deploy AI Agent](/techniques/AML.T0103)

- Updated existing techniques

  - [LLM Prompt Obfuscation](/techniques/AML.T0068)
  - [AI Supply Chain Compromise: AI Software](/techniques/AML.T0010.001)

###### Case Studies

- Added new case studies

  - [Data Exfiltration via an MCP Server used by Cursor](/studies/AML.CS0045)
  - [Data Destruction via Indirect Prompt Injection Targeting Claude Computer-Use](/studies/AML.CS0046)
  - [Malicious AI Agent Discovered in Amazon Q VS Code Extension ](/studies/AML.CS0047)

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

  - [Lateral Movement](/tactics/AML.TA0015)

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

  - [Vulnerability Scanning](/mitigations/AML.M0016)
  - [AI Telemetry Logging](/mitigations/AML.M0024)

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
