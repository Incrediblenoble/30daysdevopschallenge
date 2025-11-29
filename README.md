# Weather Dashboard

This script fetches weather data from the OpenWeather API, displays it, and saves it to an AWS S3 bucket.

## Features

- Fetches current weather data for a list of cities.
- Displays key weather information (temperature, feels like, humidity, conditions).
- Generates a human-readable AI summary of the weather.
- Saves the complete weather data as a JSON file to an AWS S3 bucket.
- Configurable through environment variables.
- Accepts a list of cities as command-line arguments.
- Comprehensive unit tests with `moto` to mock AWS services.

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/weather-dashboard.git
   cd weather-dashboard
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add the following:
   ```
   OPENWEATHER_API_KEY=your_openweather_api_key
   AWS_BUCKET_NAME=your_aws_s3_bucket_name
   OPENAI_API_KEY=your_openai_api_key
   ```
   Replace the placeholder values with your actual API keys and S3 bucket name.

   You will also need to have your AWS credentials configured. You can do this by setting the `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` (if applicable) environment variables, or by creating a credentials file at `~/.aws/credentials`.

## Usage

To run the script with the default list of cities (Philadelphia, Seattle, New York), simply run:
```bash
python src/weather_dashboard.py
```

To specify a custom list of cities, pass them as command-line arguments:
```bash
python src/weather_dashboard.py "Los Angeles" "Chicago" "Houston"
```

## Testing

The project includes a comprehensive test suite using `unittest` and `moto`. To run the tests, execute the following command from the root directory:
```bash
python -m unittest tests/test_weather_dashboard.py
```
