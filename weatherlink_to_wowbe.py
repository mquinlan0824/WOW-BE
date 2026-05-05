#!/usr/bin/env python3
"""
Weather Underground v2 API to WOW-BE Data Uploader
Fetches weather data from Weather Underground v2 API (PWS Observations) and sends it to WOW-BE platform.
Runs every 5 minutes via launchd on Mac.
"""

import requests
import json
import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
WEATHER_UNDERGROUND_API_URL = "https://api.weather.com/v2/pws/observations/current"
WOWBE_API_URL = "https://wow.meteo.be/api/v2/send"

# Setup logging
LOG_DIR = Path.home() / "Library" / "Logs" / "WOW-BE"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "wowbe_uploader.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_credentials():
    """Load API credentials from environment variables."""
    config = {
        'weather_underground_api_key': os.getenv('WEATHER_UNDERGROUND_API_KEY'),
        'weather_underground_station_id': os.getenv('WEATHER_UNDERGROUND_STATION_ID'),
        'wowbe_station_id': os.getenv('WOWBE_STATION_ID'),
        'wowbe_auth_key': os.getenv('WOWBE_AUTH_KEY'),
    }

    # Validate all credentials are present
    missing = [k for k, v in config.items() if not v]
    if missing:
        logger.error(f"Missing environment variables: {', '.join(missing)}")
        raise ValueError(f"Missing credentials: {', '.join(missing)}")

    return config


def fetch_weather_underground_data(config):
    """Fetch current weather data from Weather Underground API."""
    try:
        # Build the correct API URL for Weather Underground v2
        # Format: https://api.weather.com/v2/pws/observations/current?stationId=STATION_ID&format=json&units=e&apiKey=API_KEY
        api_key = config['weather_underground_api_key']
        station_id = config['weather_underground_station_id']

        params = {
            'stationId': station_id,
            'format': 'json',
            'units': 'e',  # English units (Fahrenheit)
            'apiKey': api_key
        }

        response = requests.get(WEATHER_UNDERGROUND_API_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        logger.debug(f"Weather Underground response: {json.dumps(data, indent=2)}")

        return data

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch Weather Underground data: {e}")
        raise


def format_for_wowbe(wu_data):
    """Convert Weather Underground v2 API data to WOW-BE API format."""
    try:
        # Extract the observation data from Weather Underground v2 response
        # Response structure: {"observations": [{"stationId": ..., "imperial": {...}, ...}]}
        if 'observations' not in wu_data or not wu_data['observations']:
            logger.error("No observations data in Weather Underground response")
            return None

        obs = wu_data['observations'][0]
        imperial = obs.get('imperial', {})

        wowbe_data = {}

        # Temperature (Fahrenheit)
        if 'temp' in imperial and imperial['temp'] is not None:
            wowbe_data['tempf'] = imperial['temp']

        # Humidity (%)
        if 'humidity' in obs and obs['humidity'] is not None:
            wowbe_data['humidity'] = obs['humidity']

        # Pressure - relative (sea level, inHg)
        if 'pressure' in imperial and imperial['pressure'] is not None:
            wowbe_data['baromin'] = imperial['pressure']

        # Wind speed (mph - WOW-BE expects mph, not km/h)
        if 'windSpeed' in imperial and imperial['windSpeed'] is not None:
            wowbe_data['windspeedmph'] = imperial['windSpeed']

        # Wind direction (degrees)
        if 'winddir' in obs and obs['winddir'] is not None:
            wowbe_data['winddir'] = obs['winddir']

        # Wind gust (mph - WOW-BE expects mph)
        if 'windGust' in imperial and imperial['windGust'] is not None:
            wowbe_data['windgustmph'] = imperial['windGust']

        # Rainfall rate (in/hr)
        if 'precipRate' in imperial and imperial['precipRate'] is not None:
            wowbe_data['rainin'] = imperial['precipRate']

        # Dew point (Fahrenheit)
        if 'dewpt' in imperial and imperial['dewpt'] is not None:
            wowbe_data['dewptf'] = imperial['dewpt']

        # Solar radiation (if available)
        if 'solarRadiation' in obs and obs['solarRadiation'] is not None:
            wowbe_data['solarradiation'] = obs['solarRadiation']

        # Software type (from Weather Underground)
        if 'softwareType' in obs and obs['softwareType'] is not None:
            wowbe_data['softwaretype'] = obs['softwareType']

        logger.debug(f"Formatted WOW-BE data: {json.dumps(wowbe_data, indent=2)}")
        return wowbe_data

    except (KeyError, TypeError, ValueError, IndexError) as e:
        logger.error(f"Error formatting data: {e}")
        return None


def send_to_wowbe(config, wowbe_data):
    """Send formatted data to WOW-BE API."""
    try:
        if not wowbe_data:
            logger.warning("No data to send to WOW-BE")
            return False

        data = {
            'siteid': config['wowbe_station_id'],
            'siteAuthenticationKey': config['wowbe_auth_key'],
        }

        data.update(wowbe_data)
        # Use ISO 8601 format for dateutc (WOW-BE API requirement)
        data['dateutc'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        logger.debug(f"Sending to WOW-BE: {json.dumps(data, indent=2)}")

        # Send as GET with query parameters (WOW-BE protocol)
        response = requests.get(WOWBE_API_URL, params=data, timeout=10)
        response.raise_for_status()

        logger.info(f"Successfully sent data to WOW-BE")
        return True

    except requests.exceptions.HTTPError as e:
        logger.error(f"Failed to send data to WOW-BE: {e}")
        # Log the response body if available to help debug
        try:
            logger.error(f"WOW-BE response body: {e.response.text}")
        except:
            pass
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send data to WOW-BE: {e}")
        return False


def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("Starting Weather Underground to WOW-BE uploader")

    try:
        config = load_credentials()
        logger.info(f"Loaded credentials for WOW-BE station: {config['wowbe_station_id']}")

        logger.info("Fetching data from Weather Underground...")
        wu_data = fetch_weather_underground_data(config)

        logger.info("Formatting data for WOW-BE...")
        wowbe_data = format_for_wowbe(wu_data)

        if wowbe_data:
            logger.info("Sending data to WOW-BE...")
            send_to_wowbe(config, wowbe_data)
        else:
            logger.error("Failed to format data for WOW-BE")
            return 1

        logger.info("Upload cycle completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1
    finally:
        logger.info("=" * 60)


if __name__ == '__main__':
    sys.exit(main())
