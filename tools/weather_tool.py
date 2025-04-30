import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import requests


@dataclass
class WeatherData:
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    description: str
    icon: str
    timestamp: datetime
    location: str
    uv_index: Optional[float] = None
    air_quality: Optional[int] = None


class WeatherTool:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHERMAP_API_KEY")
        if not self.api_key:
            raise ValueError("OPENWEATHERMAP_API_KEY environment variable is not set")
        self.base_url = "http://api.openweathermap.org/data/2.5"

    def _make_api_request(
        self, endpoint: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make a generic API request with error handling"""
        response = requests.get(f"{self.base_url}/{endpoint}", params=params)
        data = response.json()

        if response.status_code != 200:
            raise Exception(f"API error: {data.get('message', 'Unknown error')}")

        return data

    def _get_coordinates(self, location: str) -> Tuple[float, float]:
        """Get coordinates for a location using the geocoding API"""
        # Try different variations of the location name
        location_variations = [
            location,  # Original location
            f"{location},PK",  # With country code
            f"{location},Pakistan",  # With full country name
            location.title(),  # Title case
            location.upper(),  # Upper case
        ]

        for loc in location_variations:
            try:
                # Try direct geocoding first
                params = {"q": loc, "appid": self.api_key, "limit": 1}
                data = self._make_api_request("geo/1.0/direct", params)

                if data and len(data) > 0:
                    return data[0]["lat"], data[0]["lon"]
            except Exception:
                continue

        # If all variations fail, try the weather API as fallback
        for loc in location_variations:
            try:
                params = {"q": loc, "appid": self.api_key}
                data = self._make_api_request("weather", params)
                return data["coord"]["lat"], data["coord"]["lon"]
            except Exception:
                continue

        raise Exception(
            f"Could not find coordinates for {location}. Please check the location name and try again."
        )

    def get_current_weather(self, location: str) -> WeatherData:
        """Get current weather data for a specific location"""
        params = {"q": location, "appid": self.api_key, "units": "metric"}
        data = self._make_api_request("weather", params)

        return WeatherData(
            temperature=data["main"]["temp"],
            feels_like=data["main"]["feels_like"],
            humidity=data["main"]["humidity"],
            wind_speed=data["wind"]["speed"],
            description=data["weather"][0]["description"],
            icon=data["weather"][0]["icon"],
            timestamp=datetime.fromtimestamp(data["dt"]),
            location=location,
        )

    def get_weather_forecast(self, location: str, days: int = 5) -> List[WeatherData]:
        """Get weather forecast for the next few days"""
        lat, lon = self._get_coordinates(location)

        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
            "cnt": days * 8,  # 8 data points per day
        }

        data = self._make_api_request("forecast", params)

        forecast = []
        for item in data["list"]:
            forecast.append(
                WeatherData(
                    temperature=item["main"]["temp"],
                    feels_like=item["main"]["feels_like"],
                    humidity=item["main"]["humidity"],
                    wind_speed=item["wind"]["speed"],
                    description=item["weather"][0]["description"],
                    icon=item["weather"][0]["icon"],
                    timestamp=datetime.fromtimestamp(item["dt"]),
                    location=location,
                )
            )

        return forecast

    def get_air_quality(self, location: str) -> Dict[str, Any]:
        """Get air quality data for a location"""
        lat, lon = self._get_coordinates(location)

        params = {"lat": lat, "lon": lon, "appid": self.api_key}
        data = self._make_api_request("air_pollution", params)

        return {
            "aqi": data["list"][0]["main"]["aqi"],
            "components": data["list"][0]["components"],
        }

    def get_uv_index(self, lat: float, lon: float) -> float:
        """Get UV index for specific coordinates"""
        params = {"lat": lat, "lon": lon, "appid": self.api_key}
        data = self._make_api_request("uvi", params)
        return data["value"]

    def get_historical_air_quality(
        self, location: str, days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get historical air quality data for a location"""
        lat, lon = self._get_coordinates(location)

        historical_data = []
        for i in range(days):
            timestamp = int((datetime.now() - timedelta(days=i)).timestamp())

            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "start": timestamp,
                "end": timestamp,
            }

            try:
                data = self._make_api_request("air_pollution/history", params)
                if data["list"]:
                    historical_data.append(
                        {
                            "date": datetime.fromtimestamp(timestamp).strftime(
                                "%Y-%m-%d"
                            ),
                            "aqi": data["list"][0]["main"]["aqi"],
                            "components": data["list"][0]["components"],
                        }
                    )
            except Exception:
                continue

        return historical_data
