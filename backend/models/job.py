import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Numeric, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base, TimestampMixin
from .enums import JobTypeEnum, JobStatusEnum, PayTypeEnum

class Job(TimestampMixin, Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False)
    posted_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("employers.user_id", ondelete="SET NULL"), nullable=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"), index=True, nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    job_type: Mapped[JobTypeEnum] = mapped_column(nullable=False)
    status: Mapped[JobStatusEnum] = mapped_column(default=JobStatusEnum.DRAFT, index=True, server_default='DRAFT')
    
    vacancies: Mapped[int] = mapped_column(Integer, default=1, server_default='1')
    experience_required_years: Mapped[Optional[float]] = mapped_column(Numeric(4, 1), nullable=True)
    
    city: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(9, 6), nullable=True)
    
    pay_type: Mapped[Optional[PayTypeEnum]] = mapped_column(nullable=True)
    pay_min: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    pay_max: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True, nullable=True)

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="jobs")
    posted_by: Mapped[Optional["Employer"]] = relationship("Employer", back_populates="posted_jobs")
    category: Mapped["Category"] = relationship("Category", back_populates="jobs")
    job_requirements: Mapped[List["JobRequirement"]] = relationship("JobRequirement", back_populates="job", cascade="all, delete-orphan")
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    saved_by_workers: Mapped[List["SavedJob"]] = relationship("SavedJob", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Job {self.title} (Status: {self.status.name})>"

class JobRequirement(Base):
    __tablename__ = "job_requirements"

    job_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, server_default='true')

    job: Mapped["Job"] = relationship("Job", back_populates="job_requirements")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="job_requirements")

    def __repr__(self) -> str:
        return f"<JobRequirement Job: {self.job_id} Skill: {self.skill_id}>"
