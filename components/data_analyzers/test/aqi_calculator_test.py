from components.data_analyzers.src.aqi_calculator import AQICalculator
import unittest


class TestAQICalculator(unittest.TestCase):

    def setUp(self):
        self.aqi_calculator = AQICalculator()

    def test_calculate_aqi(self):
        self.aqi_calculator._pm25 = 24
        self.aqi_calculator._pm10 = 25

        aqi = self.aqi_calculator.calculate_aqi()

        assert aqi == 78.76

    def test_no_pollutants_provided(self):
        with self.assertRaises(ValueError):
            self.aqi_calculator.calculate_aqi()
