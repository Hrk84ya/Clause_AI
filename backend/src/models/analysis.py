import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    risk_score: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    summary_brief: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_standard: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_detailed: Mapped[str | None] = mapped_column(Text, nullable=True)
    anomalies: Mapped[dict | None] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    document = relationship("Document", back_populates="analyses")
    clauses = relationship("Clause", back_populates="analysis", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_analyses_document_id", "document_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Analysis(id={self.id}, document_id={self.document_id}, risk_score={self.risk_score})>"


class Clause(Base):
    __tablename__ = "clauses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    analysis_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
    )
    clause_type: Mapped[str] = mapped_column(String(100), nullable=False)
    verbatim_text: Mapped[str] = mapped_column(Text, nullable=False)
    section_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    plain_english: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    risk_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    analysis = relationship("Analysis", back_populates="clauses")

    __table_args__ = (
        Index("idx_clauses_analysis_id", "analysis_id"),
        Index("idx_clauses_risk_level", "risk_level"),
    )

    def __repr__(self) -> str:
        return f"<Clause(id={self.id}, type={self.clause_type}, risk={self.risk_level})>"
