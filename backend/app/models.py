from datetime import date, datetime, timezone
from sqlalchemy import Date, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

class YieldObservation(Base):
    __tablename__ = "yield_observations"
    __table_args__ = (UniqueConstraint("observation_date", "tenor", name="uq_yield_date_tenor"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    observation_date: Mapped[date] = mapped_column(Date, index=True)
    tenor: Mapped[str] = mapped_column(String(8), index=True)
    maturity_years: Mapped[float] = mapped_column(Float)
    yield_percent: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(40), default="US Treasury")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
