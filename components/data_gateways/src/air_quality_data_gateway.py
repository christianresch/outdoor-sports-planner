from sqlalchemy import create_engine, DateTime, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from components.database_support.air_quality_record import AirQualityRecord
from typing import Optional, List
from datetime import datetime

class AirQualityDataGateway():

    def __init__(self, db_path: str = "sqlite:///air_quality.db"):
        self.engine = create_engine(db_path, echo=True)
        self.db_path = db_path

        # TODO Work out the best way to setup the database, most likely as part of the CI/CD pipeline or using something like alembic.
    def create(self):
        AirQualityRecord.metadata.create_all(self.engine)

    def insert_air_quality_data(self,
                            city: Optional[str],
                            latitude: float,
                            longitude: float,
                            aqi: Optional[float] = None,
                            dominantpol: Optional[str] = None,
                            pm25: Optional[float] = None,
                            pm10: Optional[float] = None,
                            o3: Optional[float] = None,
                            uvi: Optional[float] = None,
                            recorded_at: Optional[datetime] = None,
                            raise_integrity_error: bool = False,
                            raise_runtime_error: bool = False):
        recorded_at = recorded_at if recorded_at else datetime.now()
        record = AirQualityRecord(
            city=city,
            latitude=latitude,
            longitude=longitude,
            aqi=aqi,
            dominantpol=dominantpol,
            pm25=pm25,
            pm10=pm10,
            o3=o3,
            uvi=uvi,
            recorded_at=recorded_at
        )

        with Session(self.engine) as session:
            try:
                session.add(record)

                # Hook for testing purposes
                if raise_runtime_error:
                    raise RuntimeError("Simulated error during transaction")

                session.commit()
            except IntegrityError as e:
                session.rollback()
                if raise_integrity_error:
                    raise e
                else:
                    raise ValueError(
                        f"Duplicate entry for city '{record.city}' and datetime '{record.recorded_at}'")
            except RuntimeError as e:
                session.rollback()
                raise e  # Re-raise the exception to ensure it propagates

    def get_air_quality_data_by_city(self, city: str, recorded_at: Optional[datetime] = None) -> List[AirQualityRecord]:
        if recorded_at:
            with Session(self.engine) as session:
                # Given the ORM, this should always only return one entry given that city+recorded_at is a unique identifier (and there are test to ensure this). But query with .all() should return this as a list with one entry.
                record = session.query(AirQualityRecord).filter(
                    and_(AirQualityRecord.city == city,
                         AirQualityRecord.recorded_at == recorded_at)
                ).all()
                return record
        else:
            with Session(self.engine) as session:
                records = session.query(AirQualityRecord).filter(AirQualityRecord.city == city).all()
                return records

    def get_air_quality_data_by_coords(self, latitude: float, longitude: float,
                                   recorded_at: Optional[datetime] = None) -> List[AirQualityRecord]:
        if recorded_at:
            with Session(self.engine) as session:
                record = session.query(AirQualityRecord).filter(
                    and_(AirQualityRecord.latitude == latitude,
                         AirQualityRecord.longitude == longitude,
                         AirQualityRecord.recorded_at == recorded_at)
                ).all()
                return record
        else:
            with Session(self.engine) as session:
                records = session.query(AirQualityRecord).filter(
                    and_(AirQualityRecord.latitude == latitude,
                         AirQualityRecord.longitude == longitude)
                ).all()
                return records

    def get_weather_data_by_id(self, id: int) -> AirQualityRecord:
        with Session(self.engine) as session:
            record = session.get(AirQualityRecord, id)
            return record

    def delete_weather_data(self, record: AirQualityRecord):
        with Session(self.engine) as session:
            session.delete(record)  # Marks the record for deletion
            session.commit()  # Executes the DELETE statement in the database
