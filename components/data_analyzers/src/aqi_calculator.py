from typing import Optional
import math
import os
import json


class AQICalculator:

    _pollutants_list = ["_pm25", "_pm10"]

    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _pollutant_breakpoints_path = os.path.join(
        _current_dir, "pollutant_breakpoints.json"
    )

    with open(_pollutant_breakpoints_path, "r") as file:
        pollutant_breakpoints = json.load(file)

    _pm25_breakpoints = pollutant_breakpoints["pm25_breakpoints"]
    _pm10_breakpoints = pollutant_breakpoints["pm10_breakpoints"]
    # o3_breakpoints = pollutant_breakpoints['o3_breakpoints']

    def __init__(
        self,
        dominantpol: Optional[str] = None,
        pm25: Optional[float] = None,
        pm10: Optional[float] = None,
        pollutant_breakpoints_path: Optional[str] = None,
    ):
        if dominantpol:
            self._dominantpol = dominantpol
        if pm25:
            self._pm25 = round(pm25, 1)
        if pm10:
            self._pm10 = math.trunc(pm10)
        # In case o3 should be later added
        # if o3:
        # self.o3 = round(o3, 3)

        # Uses data from the US EPA
        # Determine the path to the JSON file
        if pollutant_breakpoints_path is not None:
            # Load the pollutant breakpoints
            with open(pollutant_breakpoints_path, "r") as file:
                pollutant_breakpoints = json.load(file)

            self._pm25_breakpoints = pollutant_breakpoints["pm25_breakpoints"]
            self._pm10_breakpoints = pollutant_breakpoints["pm10_breakpoints"]
            # self._o3_breakpoints = pollutant_breakpoints['o3_breakpoints']

    def calculate_aqi(self) -> float:

        if all(v not in self.__dict__.keys() for v in self._pollutants_list):
            raise ValueError(
                "No pollutants provided. "
                "You need to provide at least one of "
                "PM25, PM10, O3 or UVI."
            )

        """
        Calculations according to US EPA:
        https://document.airnow.gov/
        technical-assistance-document-for-the-reporting-of-daily-air-quailty.pdf
        """

        aqi: float = 0

        for pollutant in self._pollutants_list:
            pollutant_concentration = getattr(self, pollutant, None)

            pollutant_aqi = self.__calculate_pollutant_aqi__(
                pollutant, pollutant_concentration
            )

            if pollutant_aqi > aqi:
                aqi = pollutant_aqi

        return aqi

    def __calculate_pollutant_aqi__(
        self, pollutant: str, pollutant_concentration: float
    ) -> float:
        breakpoints = getattr(self, f"{pollutant}_breakpoints", None)
        if breakpoints is None:
            raise AttributeError(f"No breakpoints found for pollutant: {pollutant}")

        for aqi_level in breakpoints:
            lower_bound = breakpoints[aqi_level]["Range"][0]
            upper_bound = breakpoints[aqi_level]["Range"][1]

            if upper_bound is None:
                breakpoint_low = lower_bound
                breakpoint_high = upper_bound

                aqi_low = breakpoints[aqi_level]["AQI"][0]
                aqi_high = breakpoints[aqi_level]["AQI"][1]
            else:
                if (
                    pollutant_concentration <= upper_bound
                    and pollutant_concentration >= lower_bound
                ):
                    breakpoint_low = lower_bound
                    breakpoint_high = upper_bound

                    aqi_low = breakpoints[aqi_level]["AQI"][0]
                    aqi_high = breakpoints[aqi_level]["AQI"][1]
                    break

        if breakpoint_high is None:
            return 301

        pollutant_aqi = ((aqi_high - aqi_low) / (breakpoint_high - breakpoint_low)) * (
            pollutant_concentration - breakpoint_low
        ) + aqi_low

        return round(pollutant_aqi, 2)

    def set_pm25(self, pm25: float):
        self._pm25 = pm25

    def get_pm25(self) -> float:
        return self._pm25

    def set_pm10(self, pm10: float):
        self._pm10 = pm10

    def get_pm10(self) -> float:
        return self._pm10

    def set_pm25_breakpoints(self, pm25_breakpoints: dict):
        self._pm25_breakpoints = pm25_breakpoints

    def get_pm25_breakpoints(self) -> dict:
        return self._pm25_breakpoints

    def set_pm10_breakpoints(self, pm10_breakpoints: dict):
        self._pm10_breakpoints = pm10_breakpoints

    def get_pm10_breakpoints(self) -> dict:
        return self._pm10_breakpoints
