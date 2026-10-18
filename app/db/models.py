from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import func, ForeignKey, ARRAY, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass


class ResumeORM(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    raw_text: Mapped[str]
    analysis: Mapped[dict | None] = mapped_column(
        JSONB
    )

    matching_results: Mapped[list["MatchingResultORM"]] = relationship(
        back_populates="resume"
    )

    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    update_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )


class MatchingResultORM(Base):
    __tablename__ = "matching_results"

    id: Mapped[int] = mapped_column(primary_key=True)

    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"))
    vacancy_id: Mapped[int] = mapped_column(ForeignKey("vacancies.id"))

    resume : Mapped["ResumeORM"] = relationship(back_populates="matching_results")
    vacancy : Mapped["VacancyORM"] = relationship(back_populates="matching_results")

    bm25_score: Mapped[float]
    embedding_score: Mapped[float]
    llm_score: Mapped[float]
    total_score: Mapped[float]

    created_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    update_at : Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )


class CompanyORM(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    hh_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str]
    description: Mapped[str]
    logo: Mapped[str]
    site_url: Mapped[str]

    vacancies: Mapped[list["VacancyORM"]] = relationship(back_populates="company")


class VacancyORM(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    hh_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str | None]
    area: Mapped[str | None]
    experience: Mapped[str | None]
    response_letter_required: Mapped[bool | None]
    description: Mapped[str | None]

    salary_from: Mapped[int | None]
    salary_to: Mapped[int | None]
    salary_mode: Mapped[str | None]
    currency: Mapped[str | None]

    work_formats: Mapped[list[str] | None] = mapped_column(
        ARRAY(String)
    )
    work_schedule_by_days: Mapped[list[str] | None] = mapped_column(
        ARRAY(String)
    )
    working_hours: Mapped[list[str] | None] = mapped_column(
        ARRAY(String)
    )

    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("companies.id")
    )
    company: Mapped['CompanyORM | None'] = relationship(
        back_populates="vacancies"
    )

    matching_results: Mapped[list["MatchingResultORM"]] = relationship(
        back_populates="vacancy"
    )
