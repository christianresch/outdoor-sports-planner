import pytest
from applications.data_collector_server.src.weather_data_collector_server import (
    RequestData,
)


def test_RequestData_valid():
    data = RequestData(latitude=1, longitude=2)
    data.validate()


def test_RequestData_invalid():
    lat_data = RequestData(latitude=1)

    with pytest.raises(
        ValueError, match="Either 'city' or 'latitude/longitude' must be provided."
    ):
        lat_data.validate()

    long_data = RequestData(longitude=1)

    with pytest.raises(
        ValueError, match="Either 'city' or 'latitude/longitude' must be provided."
    ):
        long_data.validate()
