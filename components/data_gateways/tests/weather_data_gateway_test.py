from components.data_gateways.src.weather_data_gateway import WeatherDataGateway
from components.database_support.weather_record import WeatherRecord
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect
from datetime import datetime

@pytest.fixture
def gateway():
    gateway = WeatherDataGateway(db_path="sqlite:///:memory:")
    gateway.create()
    return gateway

def test_database_connection(gateway):
    assert gateway.engine is not None
    assert str(gateway.engine.url) == "sqlite:///:memory:"

def test_create_weather_database(gateway):

    # Verify that the table exists
    inspector = inspect(gateway.engine)
    assert "weather_records" in inspector.get_table_names()

    # Verify schema (example columns)
    columns = inspector.get_columns("weather_records")
    column_names = [col["name"] for col in columns]
    assert "id" in column_names
    assert "city" in column_names
    assert "latitude" in column_names
    assert "longitude" in column_names
    assert "temperature" in column_names
    assert "recorded_at" in column_names

def test_insert_weather_data(gateway):
    test_datetime = datetime(2024, 11, 28, 12, 0, 0)
    gateway.insert_weather_data(city="Berlin", latitude=52.52, longitude=13.405, temperature=20.5,
                                recorded_at=test_datetime)

    gateway.insert_weather_data(city="Bogota", latitude=4.60971, longitude=-74.08175, temperature=19,
                                recorded_at=test_datetime)

    with Session(gateway.engine) as session:
        # Not using gateway.get_weather_data_by_XX method to isolate the testing
        result_berlin = session.query(WeatherRecord).filter_by(city="Berlin").first()

        assert result_berlin is not None
        assert result_berlin.city == "Berlin"
        assert result_berlin.latitude == 52.52
        assert result_berlin.longitude == 13.405
        assert result_berlin.temperature == 20.5
        assert result_berlin.recorded_at == datetime(2024, 11, 28, 12, 0, 0)

        result_bogota = session.query(WeatherRecord).filter_by(city="Bogota").first()

        assert result_bogota is not None

def test_unique_city_datetime_constraint(gateway):
    test_datetime = datetime(2024, 11, 28, 12, 0, 0)

    # Insert the first record
    gateway.insert_weather_data(city="Berlin", latitude=52.52, longitude=13.405, temperature=20.5, recorded_at=test_datetime)

    # Attempt to insert a second record with the same city and datetime
    try:
        gateway.insert_weather_data(city="Berlin", latitude=52.52, longitude=13.405, temperature=22.0, recorded_at=test_datetime)
        assert False, "Expected an IntegrityError due to duplicate city and recorded_at"
    except IntegrityError:
        pass  # Test passes, the constraint was enforced

def test_insert_weather_data_duplicate_handling(gateway):
    test_datetime = datetime(2024, 11, 28, 12, 0, 0)
    # Insert the first record
    gateway.insert_weather_data(city="Berlin", latitude=52.52, longitude=13.405, temperature=20.5, recorded_at=test_datetime)

    # Attempt to insert a duplicate record
    try:
        gateway.insert_weather_data(city="Berlin", latitude=52.52, longitude=13.405, temperature=22.0, recorded_at=test_datetime)
        assert False, "Expected a ValueError due to duplicate city and recorded_at"
    except ValueError as e:
        assert "Duplicate entry for city 'Berlin'" in str(e)

def test_get_weather_data_by_city(gateway):
    with Session(gateway.engine) as session:
        # Insert mock data directly
        record = WeatherRecord(city="Berlin", latitude=52.52, longitude=13.405, temperature=20.5,
                               recorded_at=datetime.utcnow())
        session.add(record)
        session.commit()

    results = gateway.get_weather_data_by_city(city="Berlin")

    assert results is not None
    assert len(results) == 1
    assert results[0].temperature == 20.5

def test_get_weather_data_by_coords(gateway):
    with Session(gateway.engine) as session:
        # Insert mock data directly
        record = WeatherRecord(city="Berlin", latitude=52.52, longitude=13.405, temperature=20.5,
                               recorded_at=datetime.utcnow())
        session.add(record)
        session.commit()

    results = gateway.get_weather_data_by_coords(latitude=52.52, longitude=13.405)

    assert results is not None
    assert len(results) == 1
    assert results[0].temperature == 20.5

def test_get_weather_data_by_id(gateway):
    with Session(gateway.engine) as session:
        # Insert mock data directly
        record = WeatherRecord(city="Berlin", latitude=52.52, longitude=13.405, temperature=20.5,
                               recorded_at=datetime.utcnow())
        session.add(record)
        session.commit()
        generated_id = record.id

    result = gateway.get_weather_data_by_id(id=generated_id)

    assert result is not None

    # Assert correctness
    assert result is not None
    assert result.city == "Berlin"
    assert result.latitude == 52.52
    assert result.longitude == 13.405
    assert result.temperature == 20.5
    assert result.id == generated_id

def test_query_empty_database(gateway):
    data = gateway.get_weather_data_by_city("NonExistentCity")
    assert len(data) == 0

def test_delete_weather_data(gateway):
    with Session(gateway.engine) as session:
        # Insert a record
        record = WeatherRecord(city="Berlin", latitude=52.52, longitude=13.405, temperature=20.5, recorded_at=datetime.utcnow())
        session.add(record)
        session.commit()

    # Delete using the gateway
    gateway.delete_weather_data(record)

    with Session(gateway.engine) as session:
        result = session.query(WeatherRecord).filter_by(city="Berlin").first()
        assert result is None

def test_transaction_handling(gateway):
    try:
        gateway.insert_weather_data(city="Berlin", latitude=52.52, longitude=13.405, temperature=22.0)
        raise RuntimeError("Force rollback")
    except RuntimeError:
        pass

    data = gateway.get_weather_data_by_city("Berlin")
    assert len(data) == 0  # Ensure data wasn't committed

#TODO Add test for proper timezone handling