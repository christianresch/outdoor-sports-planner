from sqlalchemy import create_engine, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from components.database_support.weather_record import WeatherRecord
from typing import Optional
from datetime import datetime

#TODO Build this with SQLAlchemy!
class WeatherDataGateway():

    def __init__(self, db_path: str = "sqlite:///weather.db"):
        self.engine = create_engine(db_path, echo=True)
        self.db_path = db_path

    def create(self):
        WeatherRecord.metadata.create_all(self.engine)

    #TODO Add all getters
    def get_weather_data_by_city(self, city: str, recorded_at: Optional[datetime]) -> WeatherRecord:
        pass

    def get_weather_data_by_coords(self, latitude: float, longitude: float, recorded_at: Optional[datetime]) -> WeatherRecord:
        pass

    def get_weather_data_by_id(self, id: int, recorded_at: Optional[datetime]) -> WeatherRecord:
        pass

    def insert_weather_data(self, city: Optional[str], latitude: float, longitude: float, temperature: float, recorded_at: Optional[datetime]):
        recorded_at = recorded_at if recorded_at else datetime.now()
        record = WeatherRecord(
            city=city,
            latitude=latitude,
            longitude=longitude,
            temperature=temperature,
            recorded_at=recorded_at
        )

        #TODO Ensure that this is the right way of inserting
        with Session(self.engine) as session:
            try:
                session.add(record)
                session.commit()
            except IntegrityError:
                session.rollback()
                raise ValueError(f"Duplicate entry for city '{record.city}' and datetime '{record.recorded_at}'")

    #TODO Implement delete
    def delete_weather_data(self, record: WeatherRecord):
        pass

