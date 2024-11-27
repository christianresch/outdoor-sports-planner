from components.data_gateways.src.weather_data_gateway import WeatherDataGateway
import sqlalchemy

def test_database_connection():
    gateway = WeatherDataGateway("sqlite:///:memory:")
    engine = gateway.__connect__()
    assert engine is not None
    assert str(engine.url) == "sqlite:///:memory:"

def test_setup_weather_database():
    gateway = WeatherDataGateway("sqlite:///:memory:")
    gateway.setup_weather_database()

    # Verify that the table exists
    inspector = sqlalchemy.inspect(gateway.__connect__())
    assert "weather_data" in inspector.get_table_names()

    # Verify schema (example columns)
    columns = inspector.get_columns("weather_data")
    column_names = [col["name"] for col in columns]
    assert "id" in column_names
    assert "temperature" in column_names
    assert "humidity" in column_names
    assert "city" in column_names

def test_insert_weather_data():
    gateway = WeatherDataGateway("sqlite:///:memory:")
    gateway.setup_weather_database()
    gateway.insert_weather_data({"city": "Berlin", "temperature": 22, "humidity": 75})

    # Verify data insertion
    with gateway.__connect__().connect() as conn:
        result = conn.execute("SELECT * FROM weather_data WHERE city='Berlin'")
        row = result.fetchone()
        assert row["temperature"] == 22
        assert row["humidity"] == 75

def test_get_weather_data():
    gateway = WeatherDataGateway("sqlite:///:memory:")
    gateway.setup_weather_database()
    gateway.insert_weather_data({"city": "Berlin", "temperature": 22, "humidity": 75})
    gateway.insert_weather_data({"city": "Munich", "temperature": 20, "humidity": 70})

    data = gateway.get_weather_data("Berlin")
    assert data["city"] == "Berlin"
    assert data["temperature"] == 22
    assert data["humidity"] == 75

def test_delete_weather_data():
    gateway = WeatherDataGateway("sqlite:///:memory:")
    gateway.setup_weather_database()
    gateway.insert_weather_data({"city": "Berlin", "temperature": 22, "humidity": 75})

    gateway.delete_weather_data("Berlin")

    with gateway.__connect__().connect() as conn:
        result = conn.execute("SELECT * FROM weather_data WHERE city='Berlin'")
        row = result.fetchone()
        assert row is None

def test_duplicate_insertion():
    gateway = WeatherDataGateway("sqlite:///:memory:")
    gateway.setup_weather_database()
    gateway.insert_weather_data({"city": "Berlin", "temperature": 22, "humidity": 75})
    with pytest.raises(IntegrityError):  # Assuming city is a unique constraint
        gateway.insert_weather_data({"city": "Berlin", "temperature": 22, "humidity": 75})

def test_query_empty_database():
    gateway = WeatherDataGateway("sqlite:///:memory:")
    gateway.setup_weather_database()
    data = gateway.get_weather_data("NonExistentCity")
    assert data is None

def test_transaction_handling():
    gateway = WeatherDataGateway("sqlite:///:memory:")
    gateway.setup_weather_database()

    try:
        with gateway.__connect__().begin() as conn:
            gateway.insert_weather_data({"city": "Berlin", "temperature": 22, "humidity": 75})
            raise RuntimeError("Force rollback")
    except RuntimeError:
        pass

    data = gateway.get_weather_data("Berlin")
    assert data is None  # Ensure data wasn't committed