# data_pipeline/collectors/api_collector.py
import requests
import pandas as pd
import os
import json
from datetime import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OddsAPICollector:
    def __init__(self):
        self.api_key = os.getenv('ODDS_API_KEY')
        if not self.api_key:
            logger.error("ODDS_API_KEY not found in environment variables")
            raise ValueError("ODDS_API_KEY not found")
        
    def fetch_odds(self, league_id='EPL'):
        """Fetch betting odds from the Odds API"""
        url = f"https://api.the-odds-api.com/v4/sports/soccer_{league_id.lower()}/odds/"
        params = {
            'apiKey': self.api_key,
            'regions': 'uk,eu',
            'markets': 'h2h,spreads',
            'oddsFormat': 'decimal'
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            # Save raw data
            self._save_raw_data(data, league_id)
            # Process into DataFrame
            df = self._process_odds_data(data)
            return df
        else:
            logger.error(f"API error: {response.status_code} - {response.text}")
            return None
    
    def _save_raw_data(self, data, league_id):
        """Save raw API response to file"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        os.makedirs('data/raw/odds', exist_ok=True)
        filename = f'data/raw/odds/{league_id}_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(data, f)
        
        logger.info(f"Saved raw odds data to {filename}")
    
    def _process_odds_data(self, data):
        """Process odds data into a DataFrame"""
        odds_records = []
        
        for match in data:
            match_id = match.get('id')
            home_team = match.get('home_team')
            away_team = match.get('away_team')
            commence_time = match.get('commence_time')
            
            # Extract H2H odds
            for bookmaker in match.get('bookmakers', []):
                bookmaker_name = bookmaker.get('key')
                markets = bookmaker.get('markets', [])
                
                for market in markets:
                    if market.get('key') == 'h2h':
                        outcomes = market.get('outcomes', [])
                        
                        home_odds = next((o.get('price') for o in outcomes if o.get('name') == home_team), None)
                        away_odds = next((o.get('price') for o in outcomes if o.get('name') == away_team), None)
                        draw_odds = next((o.get('price') for o in outcomes if o.get('name') == 'Draw'), None)
                        
                        odds_records.append({
                            'match_id': match_id,
                            'home_team': home_team,
                            'away_team': away_team,
                            'commence_time': commence_time,
                            'bookmaker': bookmaker_name,
                            'home_win_odds': home_odds,
                            'draw_odds': draw_odds,
                            'away_win_odds': away_odds
                        })
        
        return pd.DataFrame(odds_records)


class WeatherAPICollector:
    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY')
        if not self.api_key:
            logger.error("WEATHER_API_KEY not found in environment variables")
            raise ValueError("WEATHER_API_KEY not found")
    
    def fetch_match_weather(self, match_date, stadium_location):
        """Fetch weather data for a specific match"""
        # Historical weather data for completed matches
        is_historical = match_date < datetime.now()
        
        if is_historical:
            url = f"https://api.weatherapi.com/v1/history.json"
        else:
            # Forecast for upcoming matches
            url = f"https://api.weatherapi.com/v1/forecast.json"
            
        params = {
            'key': self.api_key,
            'q': stadium_location,
            'dt': match_date.strftime('%Y-%m-%d')
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            # Save raw data
            self._save_raw_data(data, stadium_location, match_date)
            # Process data
            return self._process_weather_data(data, match_date, is_historical)
        else:
            logger.error(f"Weather API error: {response.status_code} - {response.text}")
            return None
    
    def _save_raw_data(self, data, location, date):
        """Save raw weather data"""
        timestamp = date.strftime('%Y%m%d')
        location_slug = location.lower().replace(' ', '_')
        
        os.makedirs('data/raw/weather', exist_ok=True)
        filename = f'data/raw/weather/{location_slug}_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(data, f)
            
        logger.info(f"Saved raw weather data to {filename}")
    
    def _process_weather_data(self, data, match_date, is_historical):
        """Process weather data into a dictionary"""
        if is_historical:
            # Extract from historical data
            day_data = data.get('forecast', {}).get('forecastday', [{}])[0]
            hour_data = self._find_match_hour_data(day_data.get('hour', []), match_date)
        else:
            # Extract from forecast data
            forecast_day = data.get('forecast', {}).get('forecastday', [{}])[0]
            hour_data = self._find_match_hour_data(forecast_day.get('hour', []), match_date)
        
        if not hour_data:
            return None
            
        return {
            'date': match_date.strftime('%Y-%m-%d'),
            'temperature_c': hour_data.get('temp_c'),
            'condition': hour_data.get('condition', {}).get('text'),
            'wind_kph': hour_data.get('wind_kph'),
            'humidity': hour_data.get('humidity'),
            'precipitation_mm': hour_data.get('precip_mm'),
            'is_day': hour_data.get('is_day')
        }
    
    def _find_match_hour_data(self, hours, match_datetime):
        """Find the closest hour data to the match time"""
        match_hour = match_datetime.hour
        
        # Find exact match or closest hour
        exact_match = next((h for h in hours if datetime.fromisoformat(h.get('time').replace('Z', '+00:00')).hour == match_hour), None)
        
        if exact_match:
            return exact_match
            
        # If no exact match, find closest
        closest_hour = min(hours, key=lambda h: abs(datetime.fromisoformat(h.get('time').replace('Z', '+00:00')).hour - match_hour))
        return closest_hour