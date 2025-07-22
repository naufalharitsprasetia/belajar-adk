import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import requests


def get_weather(city: str) -> dict:
    """
    Retrieves the current weather report for a specified city using the Open-Meteo API.
    """
    try:
        geolocator = Nominatim(user_agent="weather_app")
        location = geolocator.geocode(city)
        if not location:
            return {
                "status": "error",
                "error_message": f"Could not find the city: {city}.",
            }

        latitude = location.latitude
        longitude = location.longitude

        url = "https://api.open-meteo.com/v1/forecast"
        params = {"latitude": latitude, "longitude": longitude, "current_weather": True}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "current_weather" not in data:
            return {
                "status": "error",
                "error_message": f"Weather data not available for {city}.",
            }

        weather = data["current_weather"]
        temperature_c = weather["temperature"]
        wind_speed = weather["windspeed"]
        weather_code = weather["weathercode"]

        report = (
            f"The current temperature in {city} is {temperature_c:.1f}°C "
            f"with a wind speed of {wind_speed} km/h. "
            f"Weather code: {weather_code}."
        )

        return {"status": "success", "report": report}

    except requests.exceptions.RequestException as req_err:
        return {"status": "error", "error_message": f"Request error: {req_err}"}
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"An unexpected error occurred: {e}",
        }


def get_current_time(city: str) -> dict:
    """
    Returns the current time in a specified city.
    """
    try:
        geolocator = Nominatim(user_agent="city_time_app")
        tf = TimezoneFinder()

        location = geolocator.geocode(city)
        if not location:
            return {
                "status": "error",
                "error_message": f"Could not find the city: {city}.",
            }

        timezone_name = tf.timezone_at(lng=location.longitude, lat=location.latitude)
        if not timezone_name:
            return {
                "status": "error",
                "error_message": f"Could not determine the timezone for {city}.",
            }

        tz = ZoneInfo(timezone_name)
        now = datetime.datetime.now(tz)
        report = (
            f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
        )
        return {"status": "success", "report": report}

    except Exception as e:
        return {"status": "error", "error_message": str(e)}


def get_travel_info(city: str, info_type: str) -> dict:
    """
    Provides simulated travel information for a specified city.
    """
    city_lower = city.lower()
    info_type_lower = info_type.lower()

    # --- SIMULATED DATA ---
    travel_data = {
        "london": {
            "power outlets": "Type G (three rectangular pins). Standard voltage 230V, frequency 50Hz.",
            "culture": "A culture of politeness, orderly queues, afternoon tea, and pub culture. Greet with 'excuse me' or 'sorry' when interacting. Respect personal space.",
            "transportation": "Extensive public transportation (Tube, bus). Oyster card or contactless payment is recommended. Iconic black cabs.",
        },
        "tokyo": {
            "power outlets": "Types A and B (two or three flat pins). Standard voltage 100V, frequency 50Hz or 60Hz (depending on the region).",
            "culture": "Highly values politeness, order, and cleanliness. Do not tip. Remove shoes in homes and some restaurants. Respect queues.",
            "transportation": "Highly efficient train and metro system. The Japan Rail Pass can be cost-effective. Be mindful of rush hour.",
        },
        "new york": {
            "power outlets": "Types A and B (two or three flat pins). Standard voltage 120V, frequency 60Hz.",
            "culture": "Fast-paced, diverse, and direct. Don't hesitate to speak up. Tipping is common in restaurants and services. Rich theater and art scene.",
            "transportation": "24-hour metro (subway) system. Yellow cabs. Walking is a popular way to explore.",
        },
        "paris": {
            "power outlets": "Type E (two round pins with a grounding hole). Standard voltage 230V, frequency 50Hz.",
            "culture": "Values art, fashion, and cuisine. Greet with 'Bonjour' or 'Bonsoir'. Enjoy coffee at cafes and picnics in parks. Elegance is appreciated.",
            "transportation": "The Metro is very efficient. T+ tickets for bus, metro, and tram. Walking is the best way to see the sights.",
        },
        "surabaya": {
            "power outlets": "Types C and F (two round pins). Standard voltage 230V, frequency 50Hz.",
            "culture": "Surabayans are known to be friendly and direct. Local culinary delights (rujak cingur, lontong balap). Uses Indonesian and Javanese languages.",
            "transportation": "Public transport like the Suroboyo Bus. Taxis and online ride-hailing are very popular. Traffic can be dense.",
        },
        "ponorogo": {
            "power outlets": "Types C and F (two round pins). Standard voltage 230V, frequency 50Hz.",
            "culture": "Ponorogo dikenal sebagai kota Reog. Local culinary delights (nasi pecel, dawet jabung. Uses Indonesian and Javanese languages.",
            "transportation": "Public transport like the Suroboyo Bus. Taxis and online ride-hailing are very popular. Traffic can be dense.",
        },
    }
    # --- END SIMULATED DATA ---

    try:
        if city_lower not in travel_data:
            return {
                "status": "error",
                "error_message": f"Sorry, I don't have specific travel information for {city} yet. You can try major cities like London, Tokyo, New York, or Paris.",
            }

        city_info = travel_data[city_lower]

        if info_type_lower in city_info:
            report = f"For {info_type} in {city}: {city_info[info_type_lower]}"
            return {"status": "success", "report": report}
        else:
            found_info_key = None
            for key in city_info.keys():
                if info_type_lower in key.lower() or key.lower() in info_type_lower:
                    found_info_key = key
                    break

            if found_info_key:
                report = f"For {info_type} in {city}: {city_info[found_info_key]}"
                return {"status": "success", "report": report}
            else:
                available_info = ", ".join(city_info.keys())
                return {
                    "status": "error",
                    "error_message": f"Sorry, I don't have information about '{info_type}' for {city}. Available information includes: {available_info}.",
                }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"An error occurred while fetching travel information: {str(e)}",
        }


# Agent Definition
root_agent = Agent(
    name="nhp_travel_buddy_agent",
    model="gemini-1.5-flash-002",
    description="An intelligent agent that functions as a travel buddy. It can provide weather, time, and practical guides for destination cities.",
    instruction="You are a friendly and helpful travel buddy agent. You can answer user questions about the weather and time in a city, and provide travel guides such as information on power outlets, local culture, and transportation in the destination city. Provide relevant and practical answers for travelers.",
    tools=[get_weather, get_current_time, get_travel_info],
)
