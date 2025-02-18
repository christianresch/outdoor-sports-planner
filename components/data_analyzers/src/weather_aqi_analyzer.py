from components.data_collectors.src.weather_data_collector import WeatherForecast
from components.data_collectors.src.air_quality_data_collector import AirQualityData
from components.data_analyzers.src.aqi_calculator import AQICalculator
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
import json
import os
from loguru import logger


class WeatherAQIAnalyzer:

    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _aqi_categories_path = os.path.join(_current_dir, "aqi_categories.json")

    with open(_aqi_categories_path, "r") as file:
        aqi_categories = json.load(file)

    def __init__(
        self,
        weather_forecast: Optional[List[WeatherForecast]] = None,
        air_quality_forecast: Optional[AirQualityData] = None,
    ):
        if weather_forecast:
            self._weather_forecast = weather_forecast

        if air_quality_forecast:
            self._air_quality_forecast = air_quality_forecast

    def predict_best_outdoor_sports_day(self) -> List[datetime]:
        """
        :return: List[dict] with Dict.keys = [date: datetime.date, aqi: float,
        aqi_category: str,
        temperature_2m_max: float,
        sunshine_duration: float,
        precipitation_hours: float]

        A list of days, ordered by the potential to do outdoor sports, alongside their
        AQI and weather predictions.

        Uses:
        :self.weather_forecast: A list of weather forecasts for the coming days.
        :self.air_quality_forecast: A list of air quality forecasts with predicted
        PM2.5 and PM10 pollutant values

        How is the return value generated?
        1. Daily AQIs are calculated.
        2. Days are ordered by AQI category
        3. These days are ordered by the predicted weather in order of
            a) Precipitation hours
            b) Temperature
            c) Sunshine hours
        """

        logger.debug(
            f"Analyzing AQI and weather data for {self._air_quality_forecast['city']}"
        )

        daily_aqi = self._calculate_daily_aqi(self._air_quality_forecast)

        aqi_ordered = sorted(daily_aqi.items(), key=lambda item: item[1])

        aqi_categorized = []

        for date, aqi in aqi_ordered:
            category = ""

            for key in self.aqi_categories:
                lower_bound = self.aqi_categories[key]["lower_bound"]
                upper_bound = self.aqi_categories[key]["upper_bound"]
                if upper_bound is None and aqi >= lower_bound:
                    category = self.aqi_categories[key]["level"]
                    break
                elif lower_bound <= aqi <= upper_bound:
                    category = self.aqi_categories[key]["level"]
                    break

            if isinstance(date, str):
                date = datetime.fromisoformat(date)

            aqi_categorized.append(
                {"date": date.date(), "aqi": aqi, "category": category}
            )

        aqi_df = pd.DataFrame(aqi_categorized)
        aqi_df["date"] = pd.to_datetime(aqi_df["date"])

        weather_df = pd.DataFrame(self._weather_forecast)
        weather_df["date"] = pd.to_datetime((weather_df["date"]))
        weather_df["date"] = weather_df["date"].dt.tz_convert(None)
        weather_df["date"] = weather_df["date"].dt.date
        weather_df["date"] = pd.to_datetime(weather_df["date"])

        data = pd.merge(aqi_df, weather_df, on="date", how="left")

        logger.debug(f"Merged data: {data.head()}")

        today = self._get_today()

        data = data[data["date"] >= pd.to_datetime(today)]

        # In case, no predictions for only hazardous days should be implemented
        # if (data["category"] >= 4).all():
        #    return []

        # data = data[data['category'] < 4]

        data.sort_values(
            by=[
                "category",
                "precipitation_hours",
                "temperature_2m_max",
                "sunshine_duration",
            ],
            ascending=[True, True, False, False],
            inplace=True,
        )

        data["date"] = data["date"].dt.strftime("%Y-%m-%d")

        data = data.replace({float("nan"): None})

        result = data.to_dict(orient="records")

        logger.debug(f"Analysis results: {result}")

        return result

    def _calculate_daily_aqi(self, air_quality_forecast: AirQualityData) -> Dict:
        daily_aqi = {}

        pm25_forecast = air_quality_forecast["pm25_forecast"]
        pm10_forecast = air_quality_forecast["pm10_forecast"]

        combined_air_quality_data = {}

        for forecast in pm25_forecast:
            date = forecast["date"]
            pm25 = forecast["avg"]

            combined_air_quality_data[date] = {}
            combined_air_quality_data[date]["pm25"] = pm25

        for forecast in pm10_forecast:
            date = forecast["date"]
            pm10 = forecast["avg"]

            # In case there are pm10 but no pm25 forecasts for a given date
            combined_air_quality_data[date]["pm10"] = pm10

        for date, pollutant_forecasts in combined_air_quality_data.items():

            if "pm25" in pollutant_forecasts and "pm10" in pollutant_forecasts:
                aqi_calculator = AQICalculator(
                    pm25=pollutant_forecasts["pm25"], pm10=pollutant_forecasts["pm10"]
                )
            elif "pm25" in pollutant_forecasts:
                aqi_calculator = AQICalculator(pm25=pollutant_forecasts["pm25"])
            elif "pm10" in pollutant_forecasts:
                aqi_calculator = AQICalculator(pm10=pollutant_forecasts["pm10"])
            else:
                raise ValueError("No PM data found in pollutant_forecast")

            aqi = aqi_calculator.calculate_aqi()

            daily_aqi[date] = aqi

        return daily_aqi

    def _get_today(self) -> datetime.date:
        return datetime.today().date()

    def set_air_quality_forecast(self, air_quality_forecast: AirQualityData):
        self._air_quality_forecast = air_quality_forecast

    def get_air_quality_forecast(self) -> AirQualityData:
        return self._air_quality_forecast

    def set_weather_forecast(self, weather_forecast: List[WeatherForecast]):
        self._weather_forecast = weather_forecast

    def get_weather_forecast(self) -> List[WeatherForecast]:
        return self._weather_forecast
