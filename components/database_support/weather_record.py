from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    recorded_at = Column(DateTime(timezone=True), nullable=False)

    # Add a unique constraint for city and recorded_at
    __table_args__ = (
        UniqueConstraint("city", "recorded_at", name="unique_city_recorded_at"),
    )
