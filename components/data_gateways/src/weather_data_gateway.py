from sqlalchemy import create_engine, DateTime, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from components.database_support.weather_record import WeatherRecord
from typing import Optional, List
from datetime import datetime

class WeatherDataGateway():

    def __init__(self, db_path: str = "sqlite:///weather.db"):
        self.engine = create_engine(db_path, echo=True)
        self.db_path = db_path

    def create(self):
        WeatherRecord.metadata.create_all(self.engine)

    def insert_weather_data(self,
                            city: Optional[str],
                            latitude: float,
                            longitude: float,
                            temperature: float,
                            recorded_at: Optional[datetime] = None,
                            raise_integrity_error: bool = False,
                            raise_runtime_error: bool = False):
        recorded_at = recorded_at if recorded_at else datetime.now()
        record = WeatherRecord(
            city=city,
            latitude=latitude,
            longitude=longitude,
            temperature=temperature,
            recorded_at=recorded_at
        )

        with Session(self.engine) as session:
            try:
                print("Adding record to session...")
                session.add(record)

                #Hook for testing purposes
                if raise_runtime_error:
                    raise RuntimeError("Simulated error during transaction")

                session.commit()
                print("Record committed.")
            except IntegrityError as e:
                print("Rolling back due to IntegrityError")
                session.rollback()
                if raise_integrity_error:
                    print(f"Exception type: {type(e)}")
                    raise e
                else:
                    raise ValueError(f"Duplicate entry for city '{record.city}' and datetime '{record.recorded_at}'")
            except RuntimeError as e:
                print("Rolling back due to RuntimeError")
                session.rollback()
                raise e # Re-raise the exception to ensure it propagates

    def get_weather_data_by_city(self, city: str, recorded_at: Optional[datetime] = None) -> List[WeatherRecord]:
        if recorded_at:
            with Session(self.engine) as session:
                # Given the ORM, this should always only return one entry given that city+recorded_at is a unique identifier (and there are test to ensure this). But query with .all() should return this as a list with one entry.
                record = session.query(WeatherRecord).filter(
                    and_(WeatherRecord.city == city,
                         WeatherRecord.recorded_at == recorded_at)
                ).all()
                return record
        else:
            with Session(self.engine) as session:
                records = session.query(WeatherRecord).filter(WeatherRecord.city == city).all()
                return records

    def get_weather_data_by_coords(self, latitude: float, longitude: float, recorded_at: Optional[datetime] = None) -> List[WeatherRecord]:
        if recorded_at:
            with Session(self.engine) as session:
                record = session.query(WeatherRecord).filter(
                    and_(WeatherRecord.latitude == latitude,
                         WeatherRecord.longitude == longitude,
                         WeatherRecord.recorded_at == recorded_at)
                ).all()
                return record
        else:
            with Session(self.engine) as session:
                records = session.query(WeatherRecord).filter(
                    and_(WeatherRecord.latitude == latitude,
                         WeatherRecord.longitude == longitude)
                ).all()
                return records

    def get_weather_data_by_id(self, id: int) -> WeatherRecord:
        with Session(self.engine) as session:
            record = session.get(WeatherRecord, id)
            return record

    def delete_weather_data(self, record: WeatherRecord):
        with Session(self.engine) as session:
            session.delete(record)  # Marks the record for deletion
            session.commit()  # Executes the DELETE statement in the database
