import uuid
from typing import Optional, List
from sqlalchemy import String, Text, ForeignKey, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from .base import Base, TimestampMixin

class Category(TimestampMixin, Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    skills: Mapped[List["Skill"]] = relationship("Skill", back_populates="category", cascade="all, delete-orphan")
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category {self.name}>"

class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    category: Mapped["Category"] = relationship("Category", back_populates="skills")
    worker_skills: Mapped[List["WorkerSkill"]] = relationship("WorkerSkill", back_populates="skill", cascade="all, delete-orphan")
    job_requirements: Mapped[List["JobRequirement"]] = relationship("JobRequirement", back_populates="skill", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Skill {self.name}>"

class WorkerSkill(Base):
    __tablename__ = "worker_skills"

    worker_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("workers.user_id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    years_experience: Mapped[Optional[float]] = mapped_column(Numeric(4, 1), nullable=True)

    worker: Mapped["Worker"] = relationship("Worker", back_populates="worker_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="worker_skills")

    def __repr__(self) -> str:
        return f"<WorkerSkill Worker: {self.worker_id} Skill: {self.skill_id}>"
