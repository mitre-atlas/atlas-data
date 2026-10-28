from __future__ import annotations

from datetime import date
from typing import Any, ClassVar

from sqlalchemy import (
    JSON,
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    and_,
    text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import (
    Mapped,
    foreign,
    mapped_column,
    relationship,
)

from atlas.db import Base
from atlas.enums import (
    AtlasObjectType,
    AtlasRelationshipType,
    CaseStudyType,
    DateGranularity,
    EntityType,
    SoftwareType,
    TechniqueMaturity,
)


class Version(Base):
    __tablename__ = "versions"

    version: Mapped[str] = mapped_column(primary_key=True)
    base_version: Mapped[str | None]
    created_date: Mapped[date] = mapped_column(default=date.today)
    modified_date: Mapped[date] = mapped_column(default=date.today)
    publish_date: Mapped[date | None]


class AtlasObject(Base):
    __tablename__ = "atlas_objects"
    __table_args__ = (
        ForeignKeyConstraint(
            ["version"], ["versions.version"], name="fk_atlas_objects_version"
        ),
    )

    id: Mapped[str] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str]
    references: Mapped[list | None] = mapped_column(JSON)
    created_date: Mapped[date] = mapped_column(default=date.today)
    modified_date: Mapped[date] = mapped_column(default=date.today)
    object_type: Mapped[AtlasObjectType] = mapped_column(SQLEnum(AtlasObjectType))

    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_on": "object_type",
    }

    source_relationships: Mapped[list[Relationship]] = relationship(
        "Relationship",
        foreign_keys=lambda: [Relationship.source, Relationship.version],
        primaryjoin=lambda: and_(
            AtlasObject.id == Relationship.source,
            AtlasObject.version == Relationship.version,
        ),
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    target_relationships: Mapped[list[Relationship]] = relationship(
        "Relationship",
        foreign_keys=lambda: [Relationship.target, Relationship.version],
        primaryjoin=lambda: and_(
            AtlasObject.id == Relationship.target,
            AtlasObject.version == Relationship.version,
        ),
        lazy="selectin",
        cascade="all, delete-orphan",
        overlaps="source_relationships",
    )


class Tactic(AtlasObject):
    __tablename__ = "tactics"

    id: Mapped[str] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(primary_key=True)
    attack_reference: Mapped[dict | None] = mapped_column(JSON)

    __table_args__ = (
        ForeignKeyConstraint(
            ["id", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
    )

    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_identity": AtlasObjectType.TACTIC,
    }

    techniques: Mapped[list[Technique]] = relationship(
        "Technique",
        secondary="relationships",
        primaryjoin=lambda: and_(
            Tactic.id == foreign(Relationship.target),
            Tactic.version == foreign(Relationship.version),
            Relationship.relationship_type == AtlasRelationshipType.ACHIEVES,
        ),
        secondaryjoin=lambda: and_(
            foreign(Relationship.source) == Technique.id,
            foreign(Relationship.version) == Technique.version,
        ),
        lazy="select",
        viewonly=True,
    )


class Technique(AtlasObject):
    __tablename__ = "techniques"

    id: Mapped[str] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(primary_key=True)
    maturity: Mapped[TechniqueMaturity] = mapped_column(SQLEnum(TechniqueMaturity))
    platforms: Mapped[list | None] = mapped_column(JSON)
    attack_reference: Mapped[dict | None] = mapped_column(JSON)

    __table_args__ = (
        ForeignKeyConstraint(
            ["id", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
    )

    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_identity": AtlasObjectType.TECHNIQUE,
    }

    @property
    def tactics(self) -> list[Tactic]:
        return [
            rel.target_object
            for rel in self.source_relationships
            if rel.relationship_type == AtlasRelationshipType.ACHIEVES
        ]

    @property
    def parent(self) -> Technique | None:
        for rel in self.source_relationships:
            if rel.relationship_type == AtlasRelationshipType.SPECIALIZES:
                return rel.target_object
        return None

    @property
    def subtechniques(self) -> list[Technique]:
        return [
            rel.source_object
            for rel in self.target_relationships
            if rel.relationship_type == AtlasRelationshipType.SPECIALIZES
        ]

    @property
    def mitigated_by(self) -> list[Mitigation]:
        return [
            rel.source_object
            for rel in self.target_relationships
            if rel.relationship_type == AtlasRelationshipType.MITIGATES
        ]


class Mitigation(AtlasObject):
    __tablename__ = "mitigations"

    id: Mapped[str] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(primary_key=True)
    lifecycle_phases: Mapped[list | None] = mapped_column(JSON)
    categories: Mapped[list | None] = mapped_column(JSON)
    attack_reference: Mapped[dict | None] = mapped_column(JSON)

    __table_args__ = (
        ForeignKeyConstraint(
            ["id", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
    )

    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_identity": AtlasObjectType.MITIGATION,
    }

    mitigates: Mapped[list[Technique]] = relationship(
        "Technique",
        secondary="relationships",
        primaryjoin=lambda: and_(
            Mitigation.id == foreign(Relationship.source),
            Mitigation.version == foreign(Relationship.version),
            Relationship.relationship_type == AtlasRelationshipType.MITIGATES,
        ),
        secondaryjoin=lambda: and_(
            foreign(Relationship.target) == Technique.id,
            foreign(Relationship.version) == Technique.version,
        ),
        lazy="select",
        viewonly=True,
    )


class Entity(AtlasObject):
    __tablename__ = "entities"

    id: Mapped[str] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(primary_key=True)
    entity_type: Mapped[EntityType] = mapped_column(SQLEnum(EntityType))
    associated_entities: Mapped[list | None] = mapped_column(JSON)
    attack_reference: Mapped[dict | None] = mapped_column(JSON)

    __table_args__ = (
        ForeignKeyConstraint(
            ["id", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
    )

    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_identity": AtlasObjectType.ENTITY,
    }


class Software(AtlasObject):
    __tablename__ = "software"

    id: Mapped[str] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(primary_key=True)
    software_type: Mapped[SoftwareType] = mapped_column(SQLEnum(SoftwareType))
    software_categories: Mapped[list | None] = mapped_column(JSON, default=list)
    aliases: Mapped[list | None] = mapped_column(JSON, default=list)
    attack_reference: Mapped[dict | None] = mapped_column(JSON)

    __table_args__ = (
        ForeignKeyConstraint(
            ["id", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
    )

    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_identity": AtlasObjectType.SOFTWARE,
    }


class CaseStudy(AtlasObject):
    __tablename__ = "case_studies"

    id: Mapped[str] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(primary_key=True)
    type: Mapped[CaseStudyType] = mapped_column(SQLEnum(CaseStudyType))
    actor: Mapped[str | None]
    target: Mapped[str]
    reporter: Mapped[str | None]
    start_date: Mapped[date]
    start_date_granularity: Mapped[DateGranularity] = mapped_column(
        SQLEnum(DateGranularity)
    )
    end_date: Mapped[date | None]
    end_date_granularity: Mapped[DateGranularity | None] = mapped_column(
        SQLEnum(DateGranularity)
    )

    __table_args__ = (
        CheckConstraint(
            "(end_date IS NULL AND end_date_granularity IS NULL) OR "
            "(end_date IS NOT NULL AND end_date_granularity IS NOT NULL)",
            name="ck_case_studies_end_date_pair",
        ),
        ForeignKeyConstraint(
            ["id", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
    )

    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_identity": AtlasObjectType.CASE_STUDY,
    }

    @property
    def attack_chain(self) -> list[Technique]:
        return [
            rel.target_object
            for rel in self.source_relationships
            if rel.relationship_type == AtlasRelationshipType.EMPLOYS
        ]


class Collection(AtlasObject):
    __tablename__ = "collections"

    id: Mapped[str] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["id", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
        Index("idx_collections_version_unique", "version", unique=True),
    )

    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_identity": AtlasObjectType.COLLECTION,
    }


class Matrix(AtlasObject):
    __tablename__ = "matrices"

    id: Mapped[str] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["id", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
    )

    __mapper_args__: ClassVar[dict[str, Any]] = {
        "polymorphic_identity": AtlasObjectType.MATRIX,
    }

    tactics: Mapped[list[Tactic]] = relationship(
        "Tactic",
        secondary="relationships",
        primaryjoin=lambda: and_(
            Matrix.id == foreign(Relationship.source),
            Matrix.version == foreign(Relationship.version),
            Relationship.relationship_type == AtlasRelationshipType.SEQUENCES,
        ),
        secondaryjoin=lambda: and_(
            foreign(Relationship.target) == Tactic.id,
            foreign(Relationship.version) == Tactic.version,
        ),
        lazy="select",
        viewonly=True,
    )


class FormatVersion(Base):
    __tablename__ = "format_version"

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str]
    created_date: Mapped[date] = mapped_column(default=date.today)
    modified_date: Mapped[date] = mapped_column(default=date.today)


class Relationship(Base):
    __tablename__ = "relationships"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source: Mapped[str]
    target: Mapped[str]
    version: Mapped[str]
    relationship_type: Mapped[AtlasRelationshipType] = mapped_column(
        SQLEnum(AtlasRelationshipType), index=True
    )
    description: Mapped[str | None]
    extra_fields: Mapped[dict | None] = mapped_column(JSON)

    source_object: Mapped[AtlasObject] = relationship(
        "AtlasObject",
        foreign_keys=lambda: [Relationship.source, Relationship.version],
        primaryjoin=lambda: and_(
            Relationship.source == AtlasObject.id,
            Relationship.version == AtlasObject.version,
        ),
        lazy="selectin",
        viewonly=True,
        overlaps="source_relationships",
    )

    target_object: Mapped[AtlasObject] = relationship(
        "AtlasObject",
        foreign_keys=lambda: [Relationship.target, Relationship.version],
        primaryjoin=lambda: and_(
            Relationship.target == AtlasObject.id,
            Relationship.version == AtlasObject.version,
        ),
        lazy="selectin",
        viewonly=True,
        overlaps="target_relationships",
    )

    __table_args__ = (
        CheckConstraint("source != target", name="ck_relationship_source_not_target"),
        ForeignKeyConstraint(
            ["source", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
        ForeignKeyConstraint(
            ["target", "version"],
            ["atlas_objects.id", "atlas_objects.version"],
        ),
        Index(
            "idx_unique_non_employs",
            "source",
            "target",
            "version",
            "relationship_type",
            unique=True,
            sqlite_where=text("relationship_type != 'EMPLOYS'"),
        ),
        Index(
            "idx_employs_unique",
            "source",
            "target",
            "version",
            "relationship_type",
            "extra_fields",
            unique=True,
            sqlite_where=text("relationship_type = 'EMPLOYS'"),
        ),
    )
