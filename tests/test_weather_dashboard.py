import unittest
import os
import requests
from unittest.mock import patch, MagicMock
from moto import mock_aws
import boto3
import sys

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from weather_dashboard import WeatherDashboard, get_ai_summary

class TestWeatherDashboard(unittest.TestCase):
    def setUp(self):
        """Set up the test environment."""
        self.api_key = "test_api_key"
        self.bucket_name = "test-bucket"
        os.environ['OPENWEATHER_API_KEY'] = self.api_key
        os.environ['AWS_BUCKET_NAME'] = self.bucket_name

    @patch('requests.get')
    def test_fetch_weather_success(self, mock_get):
        """Test successful weather data fetching."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"main": {"temp": 70}, "weather": [{"description": "clear sky"}]}
        mock_get.return_value = mock_response

        dashboard = WeatherDashboard(self.api_key, self.bucket_name)
        weather_data = dashboard.fetch_weather("Test City")

        self.assertIsNotNone(weather_data)
        self.assertEqual(weather_data['main']['temp'], 70)

    @patch('requests.get')
    def test_fetch_weather_failure(self, mock_get):
        """Test failed weather data fetching."""
        mock_get.side_effect = requests.exceptions.RequestException("API call failed")

        dashboard = WeatherDashboard(self.api_key, self.bucket_name)
        weather_data = dashboard.fetch_weather("Test City")

        self.assertIsNone(weather_data)

    @mock_aws
    def test_save_to_s3_success(self):
        """Test successful data saving to S3."""
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket=self.bucket_name)

        dashboard = WeatherDashboard(self.api_key, self.bucket_name)
        weather_data = {"main": {"temp": 70}, "weather": [{"description": "clear sky"}]}

        success = dashboard.save_to_s3(weather_data, "Test City")

        self.assertTrue(success)

    @mock_aws
    def test_create_bucket_if_not_exists(self):
        """Test S3 bucket creation."""
        dashboard = WeatherDashboard(self.api_key, self.bucket_name)

        # This will create the bucket
        dashboard.create_bucket_if_not_exists()

        s3 = boto3.client('s3', region_name='us-east-1')
        response = s3.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]

        self.assertIn(self.bucket_name, buckets)

    @patch('openai.OpenAI')
    def test_get_ai_summary_success(self, mock_openai_client):
        """Test successful AI summary generation."""
        mock_client_instance = mock_openai_client.return_value
        mock_client_instance.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="A beautiful day!"))]
        )

        os.environ['OPENAI_API_KEY'] = "test_openai_key"
        weather_data = {
            "name": "Test City",
            "main": {"temp": 70, "feels_like": 68, "humidity": 50},
            "weather": [{"description": "clear sky"}]
        }

        summary = get_ai_summary(weather_data)
        self.assertEqual(summary, "A beautiful day!")

    @patch('openai.OpenAI')
    def test_get_ai_summary_failure(self, mock_openai_client):
        """Test failed AI summary generation."""
        mock_client_instance = mock_openai_client.return_value
        mock_client_instance.chat.completions.create.side_effect = Exception("OpenAI API error")

        os.environ['OPENAI_API_KEY'] = "test_openai_key"
        weather_data = {
            "name": "Test City",
            "main": {"temp": 70, "feels_like": 68, "humidity": 50},
            "weather": [{"description": "clear sky"}]
        }

        summary = get_ai_summary(weather_data)
        self.assertIsNone(summary)

if __name__ == '__main__':
    unittest.main()
