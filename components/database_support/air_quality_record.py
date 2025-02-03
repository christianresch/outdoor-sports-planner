from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# Define WeatherRecord Table
class AirQualityRecord(Base):
    __tablename__ = "air_quality_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    aqi = Column(Float, nullable=True)
    dominantpol = Column(String, nullable=True)
    pm25 = Column(Float, nullable=True)
    pm10 = Column(Float, nullable=True)
    o3 = Column(Float, nullable=True)
    uvi = Column(Float, nullable=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False)

    # Add a unique constraint for city and recorded_at
    __table_args__ = (
        UniqueConstraint("city", "recorded_at", name="unique_city_recorded_at"),
    )
