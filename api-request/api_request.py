import requests

api_key = "cfbe358550a04df05ee705c1e8aa117c"
api_url = f"http://api.weatherstack.com/current?access_key={api_key}&query=New York"

# Create a function that will fetch api data and build a try and except block to handle any potential errors that may occur during the API request.
def fetch_data():
    print("Fetching weatherdata from the Weatherstack API...")
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Check if the request was successful (status code 200)
        print("API response received successfully.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occured: {e}")
        raise

# we will be using the output of this function in the next step to extract the relevant weather data and store it in a database.
# we are going to create a mock fetch data function that will return a sample response from the Weatherstack API, which we can use for testing purposes. This will allow us to test our data extraction and storage logic without making actual additional API calls, which can be useful for development and debugging.

def mock_fetch_data():
    return {'request': {'type': 'City', 'query': 'New York, United States of America', 'language': 'en', 'unit': 'm'}, 'location': {'name': 'New York', 'country': 'United States of America', 'region': 'New York', 'lat': '40.714', 'lon': '-74.006', 'timezone_id': 'America/New_York', 'localtime': '2026-03-12 05:28', 'localtime_epoch': 1773293280, 'utc_offset': '-4.0'}, 'current': {'observation_time': '09:28 AM', 'temperature': 12, 'weather_code': 143, 'weather_icons': ['https://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0006_mist.png'], 'weather_descriptions': ['Mist'], 'astro': {'sunrise': '07:13 AM', 'sunset': '07:00 PM', 'moonrise': '03:36 AM', 'moonset': '12:12 PM', 'moon_phase': 'Waning Crescent', 'moon_illumination': 44}, 'air_quality': {'co': '204.85', 'no2': '13.85', 'o3': '60', 'so2': '3.85', 'pm2_5': '2.75', 'pm10': '2.75', 'us-epa-index': '1', 'gb-defra-index': '1'}, 'wind_speed': 23, 'wind_degree': 231, 'wind_dir': 'SW', 'pressure': 1001, 'precip': 0, 'humidity': 100, 'cloudcover': 0, 'feelslike': 9, 'uv_index': 0, 'visibility': 5, 'is_day': 'no'}}