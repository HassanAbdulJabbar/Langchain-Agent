from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain.agents import AgentType, initialize_agent
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.tools import Tool

from tools.weather_tool import WeatherData, WeatherTool


class WeatherAgent:
    def __init__(self, llm):
        self.weather_tool = WeatherTool()
        self.llm = llm

        # Initialize tools
        self.tools = [
            Tool(
                name="get_current_weather",
                func=self.weather_tool.get_current_weather,
                description="Get current weather data for a specific location",
            ),
            Tool(
                name="get_weather_forecast",
                func=self.weather_tool.get_weather_forecast,
                description="Get weather forecast for the next few days",
            ),
            Tool(
                name="get_air_quality",
                func=self.weather_tool.get_air_quality,
                description="Get current air quality data for a location",
            ),
            Tool(
                name="get_historical_air_quality",
                func=self.weather_tool.get_historical_air_quality,
                description="Get historical air quality data for a location over the past week",
            ),
            Tool(
                name="get_uv_index",
                func=self.weather_tool.get_uv_index,
                description="Get UV index for specific coordinates",
            ),
        ]

        # Initialize the agent with a more flexible prompt
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
        )

        # Initialize chains for different types of analysis
        self.analysis_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["weather_data", "query"],
                template="""
                Given the following weather data and user query, provide a detailed analysis and recommendations.

                Weather Data: {weather_data}
                User Query: {query}

                Provide a comprehensive response that:
                1. Addresses the specific question
                2. Considers the weather conditions
                3. Offers relevant recommendations
                """,
            ),
        )

    def invoke(self, query: str) -> str:
        """Process a weather-related query using AI-driven analysis"""
        try:
            # Extract location from query
            location = self._extract_location(query)
            if not location:
                return "I couldn't determine the location from your query. Please specify a location name."

            # Get current weather data
            current_weather = self.weather_tool.get_current_weather(location)

            # Prepare weather data for the LLM
            weather_data = {
                "temperature": current_weather.temperature,
                "humidity": current_weather.humidity,
                "wind_speed": current_weather.wind_speed,
                "description": current_weather.description,
                "location": location,
            }

            # Add air quality data if available
            try:
                current_aqi = self.weather_tool.get_air_quality(location)
                weather_data["air_quality"] = {
                    "aqi": current_aqi["aqi"],
                    "components": current_aqi["components"],
                }
            except Exception:
                pass

            # Format the response based on the query type
            if "temperature" in query.lower():
                response = f"The current temperature in {location} is {weather_data['temperature']}°C."
            elif "rain" in query.lower():
                response = f"In {location}, the current conditions are {weather_data['description']}."
            else:
                response = f"Current weather in {location}: {weather_data['description']}, Temperature: {weather_data['temperature']}°C, Humidity: {weather_data['humidity']}%, Wind Speed: {weather_data['wind_speed']} km/h."

            return response

        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}. Please try rephrasing your question."

    def _extract_location(self, query: str) -> str:
        """Extract location from the query"""
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()

        # List of major cities in Pakistan
        pakistani_cities = [
            "Islamabad",
            "Lahore",
            "Karachi",
            "Peshawar",
            "Quetta",
            "Rawalpindi",
            "Multan",
            "Faisalabad",
            "Hyderabad",
            "Gujranwala",
        ]

        # Try to find exact city names
        for city in pakistani_cities:
            if city.lower() in query_lower:
                return city

        # If no exact match, try to find location keywords
        location_keywords = ["in", "at", "for", "to", "around", "near"]
        words = query_lower.split()

        for i, word in enumerate(words):
            if word in location_keywords and i + 1 < len(words):
                # Get the next word as potential location
                potential_location = words[i + 1].capitalize()
                # Check if it's a known city
                if potential_location in [city.lower() for city in pakistani_cities]:
                    return potential_location.capitalize()

        # Default to Islamabad if no location is specified
        return "Islamabad"

    def get_weather_recommendations(self, location: str) -> Dict[str, Any]:
        """Get personalized weather recommendations based on current conditions"""
        current_weather = self.weather_tool.get_current_weather(location)
        air_quality = self.weather_tool.get_air_quality(location)

        recommendations = {
            "outdoor_activities": self._get_outdoor_activity_recommendations(
                current_weather
            ),
            "health_alerts": self._get_health_alerts(current_weather, air_quality),
            "clothing_recommendations": self._get_clothing_recommendations(
                current_weather
            ),
            "travel_impact": self._get_travel_impact(current_weather),
        }

        return recommendations

    def _get_outdoor_activity_recommendations(self, weather: WeatherData) -> List[str]:
        """Get recommendations for outdoor activities based on weather conditions"""
        recommendations = []

        if weather.temperature > 25:
            recommendations.append("Great day for swimming or beach activities")
        elif 15 <= weather.temperature <= 25:
            recommendations.append("Perfect for hiking or outdoor sports")
        elif weather.temperature < 15:
            recommendations.append(
                "Consider indoor activities or dress warmly for outdoor activities"
            )

        if weather.wind_speed > 20:
            recommendations.append("High winds - avoid activities that require balance")

        if "rain" in weather.description.lower():
            recommendations.append("Rain expected - consider indoor activities")

        return recommendations

    def _get_health_alerts(
        self, weather: WeatherData, air_quality: Dict[str, Any]
    ) -> List[str]:
        """Get health-related alerts based on weather and air quality"""
        alerts = []

        if weather.uv_index and weather.uv_index > 6:
            alerts.append(
                f"High UV index ({weather.uv_index}) - use sunscreen and limit sun exposure"
            )

        if air_quality["aqi"] > 100:
            alerts.append(
                f"Poor air quality (AQI: {air_quality['aqi']}) - limit outdoor activities"
            )

        if weather.temperature > 30:
            alerts.append(
                "High temperature - stay hydrated and avoid strenuous activities"
            )

        if weather.temperature < 0:
            alerts.append("Freezing temperatures - dress warmly and watch for ice")

        return alerts

    def _get_clothing_recommendations(self, weather: WeatherData) -> List[str]:
        """Get clothing recommendations based on weather conditions"""
        recommendations = []

        if weather.temperature > 25:
            recommendations.append("Light clothing recommended")
        elif 15 <= weather.temperature <= 25:
            recommendations.append("Light to medium clothing appropriate")
        elif 0 <= weather.temperature < 15:
            recommendations.append("Warm clothing recommended")
        else:
            recommendations.append("Heavy winter clothing required")

        if "rain" in weather.description.lower():
            recommendations.append("Bring rain gear or umbrella")

        if weather.wind_speed > 15:
            recommendations.append(
                "Windy conditions - consider wind-resistant clothing"
            )

        return recommendations

    def _get_travel_impact(self, weather: WeatherData) -> Dict[str, Any]:
        """Get travel impact analysis based on weather conditions"""
        impact = {
            "road_conditions": "Normal",
            "flight_impact": "Normal",
            "public_transport": "Normal",
        }

        if "rain" in weather.description.lower():
            impact["road_conditions"] = "Wet roads - allow extra travel time"
            impact["flight_impact"] = "Possible delays due to rain"

        if weather.wind_speed > 30:
            impact["flight_impact"] = "Possible delays due to high winds"

        if weather.temperature < 0:
            impact["road_conditions"] = "Possible ice - drive with caution"
            impact["public_transport"] = "Possible delays due to cold weather"

        return impact
