import os
import json
import boto3
import requests
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

class WeatherDashboard:
    def __init__(self, api_key, bucket_name):
        """
        Initializes the WeatherDashboard with API key and S3 bucket name.
        """
        if not api_key or not bucket_name:
            raise ValueError("API key and bucket name must be set.")
        self.api_key = api_key
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3')

    def create_bucket_if_not_exists(self):
        """
        Creates an S3 bucket if it does not already exist.

        This function checks for the existence of the specified S3 bucket and creates it if it is not found.
        It includes error handling to gracefully manage issues that may arise during the process, such as
        permission errors or region-specific constraints. Note that for regions other than 'us-east-1',
        a `LocationConstraint` must be specified in the `create_bucket` call. This implementation
        assumes the bucket is being created in 'us-east-1' for simplicity.
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logging.info(f"Bucket '{self.bucket_name}' already exists.")
        except self.s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                logging.info(f"Bucket '{self.bucket_name}' not found. Creating it.")
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logging.info(f"Successfully created bucket '{self.bucket_name}'.")
                except Exception as create_error:
                    logging.error(f"Error creating bucket '{self.bucket_name}': {create_error}")
                    raise
            else:
                logging.error(f"Error checking for bucket '{self.bucket_name}': {e}")
                raise

    def fetch_weather(self, city):
        """Fetch weather data from OpenWeather API for a given city."""
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "imperial"
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching weather data for {city}: {e}")
            return None

    def save_to_s3(self, weather_data, city):
        """Save weather data to an S3 bucket."""
        if not weather_data:
            logging.warning("No weather data to save.")
            return False
            
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        file_name = f"weather-data/{city}-{timestamp}.json"
        
        try:
            weather_data_to_save = weather_data.copy()
            weather_data_to_save['timestamp'] = timestamp

            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=json.dumps(weather_data_to_save),
                ContentType='application/json'
            )
            logging.info(f"Successfully saved data for {city} to s3://{self.bucket_name}/{file_name}")
            return True
        except Exception as e:
            logging.error(f"Error saving data for {city} to S3: {e}")
            return False

def display_weather(weather_data):
    """Prints the weather data in a user-friendly format."""
    if not weather_data:
        return

    try:
        city = weather_data.get('name', 'Unknown City')
        temp = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        humidity = weather_data['main']['humidity']
        description = weather_data['weather'][0]['description']

        logging.info(f"Weather for {city}:")
        logging.info(f"  Temperature: {temp}°F")
        logging.info(f"  Feels like: {feels_like}°F")
        logging.info(f"  Humidity: {humidity}%")
        logging.info(f"  Conditions: {description.capitalize()}")
    except (KeyError, IndexError) as e:
        logging.error(f"Could not parse weather data: {e}")

def process_city(dashboard, city):
    """
    Fetches, displays, and saves weather data for a single city.
    """
    logging.info(f"Processing weather data for {city}...")
    weather_data = dashboard.fetch_weather(city)
    
    if weather_data:
        display_weather(weather_data)
        dashboard.save_to_s3(weather_data, city)
    else:
        logging.warning(f"Could not retrieve weather data for {city}.")

def main():
    """
    Main function to run the weather dashboard application.
    """
    parser = argparse.ArgumentParser(description="Fetch weather data and save to S3.")
    parser.add_argument('cities', metavar='CITIES', type=str, nargs='*',
                        default=["Philadelphia", "Seattle", "New York"],
                        help='A list of cities to fetch weather for.')
    args = parser.parse_args()
    
    api_key = os.getenv('OPENWEATHER_API_KEY')
    bucket_name = os.getenv('AWS_BUCKET_NAME')

    try:
        dashboard = WeatherDashboard(api_key, bucket_name)
        dashboard.create_bucket_if_not_exists()

        for city in args.cities:
            process_city(dashboard, city)
            
    except ValueError as e:
        logging.error(f"Initialization failed: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
