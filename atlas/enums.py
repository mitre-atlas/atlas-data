from __future__ import annotations

from enum import Enum


def sort_enum_values(values: list[str], enum_type: type[Enum]) -> list[str]:
    order = {member.value: index for index, member in enumerate(enum_type)}
    return sorted(values, key=lambda value: order.get(value, 10**6))


def build_enum_list[E: Enum](values: list[str], enum_type: type[E]) -> list[E]:
    return [enum_type(value) for value in sort_enum_values(values, enum_type)]


class AtlasObjectType(Enum):
    COLLECTION = "collection"
    MATRIX = "matrix"
    TACTIC = "tactic"
    TECHNIQUE = "technique"
    MITIGATION = "mitigation"
    CASE_STUDY = "case-study"
    ENTITY = "entity"
    SOFTWARE = "software"


class AtlasRelationshipType(Enum):
    SEQUENCES = "sequences"
    ACHIEVES = "achieves"
    SPECIALIZES = "specializes"
    MITIGATES = "mitigates"
    EMPLOYS = "employs"
    ATTRIBUTED_TO = "attributed-to"
    REPORTED_BY = "reported-by"
    USES = "uses"
    IMPLEMENTS = "implements"


class DateGranularity(Enum):
    YEAR = "Year"
    MONTH = "Month"
    DAY = "Day"


class TechniqueMaturity(Enum):
    FEASIBLE = "Feasible"
    DEMONSTRATED = "Demonstrated"
    REALIZED = "Realized"


class TechniquePlatformType(Enum):
    PREDICTIVE = "Predictive AI"
    GENERATIVE = "Generative AI"
    AGENTIC = "Agentic AI"
    ENTERPRISE = "Enterprise"


class MitigationCategoryType(Enum):
    POLICY = "Policy"
    TECHNICAL_AI = "Technical - AI"
    TECHNICAL_CYBER = "Technical - Cyber"


class MitigationLifecyclePhasesType(Enum):
    DATA_UNDERSTANDING = "Business and Data Understanding"
    DATA_PREPARATION = "Data Preparation"
    MODEL_ENGINEERING = "AI Model Engineering"
    MODEL_EVALUATION = "AI Model Evaluation"
    DEPLOYMENT = "Deployment"
    MONITORING = "Monitoring and Maintenance"


class CaseStudyType(Enum):
    INCIDENT = "Incident"
    EXERCISE = "Exercise"


class EntityType(Enum):
    ACTIVITY_CLUSTER = "Activity Cluster"
    ORGANIZATION = "Organization"
    TEAM = "Team"
    INDIVIDUAL = "Individual"


class ActivityPurpose(Enum):
    ADVERSARIAL_OPERATION = "Adversarial Operation"
    SECURITY_EVALUATION = "Security Evaluation"
    UNINTENDED_CONSEQUENCE = "Unintended Consequence"


class SoftwareType(Enum):
    MALWARE = "Malware"
    TOOL = "Tool"


class SoftwareCategory(Enum):
    PROGRAM = "program"
    LIBRARY = "library"
    MODEL = "model"
    SERVICE = "service"
    AI_AGENT = "ai-agent"
    AI_AGENT_FRAMEWORK = "ai-agent-framework"
    AI_AGENT_INTEGRATION = "ai-agent-integration"
    PROMPT_PACKAGE = "prompt-package"
