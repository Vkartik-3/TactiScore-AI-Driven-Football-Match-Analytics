# data_pipeline/processors/integrator.py
import pandas as pd
import numpy as np
import os
import logging
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FootballDataIntegrator:
    def __init__(self):
        db_connection_string = os.getenv('DATABASE_URL')
        if not db_connection_string:
            logger.error("DATABASE_URL not found in environment variables")
            raise ValueError("DATABASE_URL not found")
            
        self.db_engine = create_engine(db_connection_string)
        
    def full_data_refresh(self):
        """Run a complete data refresh pipeline"""
        logger.info("Starting full data refresh")
        
        try:
            # 1. Extract from all sources
            match_data = self._extract_match_data()
            odds_data = self._extract_odds_data()
            weather_data = self._extract_weather_data()
            
            if match_data.empty:
                logger.warning("No match data available")
                return False
            
            # 2. Transform and integrate
            integrated_data = self._integrate_data(match_data, odds_data, weather_data)
            
            # 3. Load to database
            self._load_integrated_data(integrated_data)
            
            logger.info("Data refresh completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error in data refresh: {str(e)}")
            return False
    
    def _extract_match_data(self):
        """Extract match data from scraped sources"""
        logger.info("Extracting match data")
        
        # Check for latest scraped data
        fbref_path = 'data/raw/fbref_matches.json'
        
        if not os.path.exists(fbref_path):
            logger.warning(f"FBref data file not found: {fbref_path}")
            # Try to load from database instead
            try:
                match_data = pd.read_sql("SELECT * FROM matches", self.db_engine)
                if not match_data.empty:
                    logger.info(f"Loaded {len(match_data)} matches from database")
                    return match_data
            except Exception as e:
                logger.error(f"Failed to load match data from database: {str(e)}")
            
            return pd.DataFrame()
        
        # Load FBref data
        try:
            fbref_data = pd.read_json(fbref_path)
            logger.info(f"Loaded {len(fbref_data)} matches from FBref")
            
            # Process and clean FBref data
            processed_data = self._process_fbref_data(fbref_data)
            return processed_data
            
        except Exception as e:
            logger.error(f"Error loading FBref data: {str(e)}")
            return pd.DataFrame()
    
    def _process_fbref_data(self, df):
        """Process and clean FBref data"""
        # Extract nested stats
        processed_data = df.copy()
        
        # Flatten stats dictionary
        if 'stats' in processed_data.columns:
            stats_df = pd.json_normalize(processed_data['stats'])
            processed_data = pd.concat([processed_data.drop('stats', axis=1), stats_df], axis=1)
        
        # Convert date to datetime
        if 'match_date' in processed_data.columns:
            processed_data['match_date'] = pd.to_datetime(processed_data['match_date'])
        
        # Standardize team names
        processed_data = self._standardize_team_names(processed_data)
        
        return processed_data
    
    def _standardize_team_names(self, df):
        """Standardize team names"""
        # Define mapping for team name variations
        team_name_mapping = {
            'Manchester Utd': 'Manchester United',
            'Man United': 'Manchester United',
            'Man Utd': 'Manchester United',
            'Manchester City': 'Manchester City',
            'Man City': 'Manchester City',
            'Tottenham': 'Tottenham Hotspur',
            'Spurs': 'Tottenham Hotspur',
            'Newcastle Utd': 'Newcastle United',
            'Newcastle': 'Newcastle United',
            # Add more mappings as needed
        }
        
        # Apply mapping to team and opponent columns
        if 'home_team' in df.columns:
            df['home_team'] = df['home_team'].map(lambda x: team_name_mapping.get(x, x))
        if 'away_team' in df.columns:
            df['away_team'] = df['away_team'].map(lambda x: team_name_mapping.get(x, x))
        if 'team' in df.columns:
            df['team'] = df['team'].map(lambda x: team_name_mapping.get(x, x))
        if 'opponent' in df.columns:
            df['opponent'] = df['opponent'].map(lambda x: team_name_mapping.get(x, x))
            
        return df
    
    def _extract_odds_data(self):
        """Extract betting odds data"""
        logger.info("Extracting odds data")
        
        odds_path = 'data/processed/latest_odds.csv'
        
        if not os.path.exists(odds_path):
            logger.warning(f"Odds data file not found: {odds_path}")
            try:
                odds_data = pd.read_sql("SELECT * FROM match_odds", self.db_engine)
                if not odds_data.empty:
                    logger.info(f"Loaded {len(odds_data)} odds records from database")
                    return odds_data
            except Exception as e:
                logger.error(f"Failed to load odds data from database: {str(e)}")
            
            return pd.DataFrame()
        
        try:
            odds_data = pd.read_csv(odds_path)
            logger.info(f"Loaded {len(odds_data)} odds records")
            return odds_data
        except Exception as e:
            logger.error(f"Error loading odds data: {str(e)}")
            return pd.DataFrame()
    
    def _extract_weather_data(self):
        """Extract weather data"""
        logger.info("Extracting weather data")
        
        weather_path = 'data/processed/match_weather.csv'
        
        if not os.path.exists(weather_path):
            logger.warning(f"Weather data file not found: {weather_path}")
            try:
                weather_data = pd.read_sql("SELECT * FROM weather_conditions", self.db_engine)
                if not weather_data.empty:
                    logger.info(f"Loaded {len(weather_data)} weather records from database")
                    return weather_data
            except Exception as e:
                logger.error(f"Failed to load weather data from database: {str(e)}")
            
            return pd.DataFrame()
        
        try:
            weather_data = pd.read_csv(weather_path)
            logger.info(f"Loaded {len(weather_data)} weather records")
            return weather_data
        except Exception as e:
            logger.error(f"Error loading weather data: {str(e)}")
            return pd.DataFrame()
    
    def _integrate_data(self, match_data, odds_data, weather_data):
        """Integrate data from different sources"""
        logger.info("Integrating data sources")
        
        # Create wide-format table with one row per match
        integrated = match_data.copy()
        
        # Integrate odds data if available
        if not odds_data.empty and 'match_id' in odds_data.columns:
            # Group by match and take mean of odds (in case of multiple bookmakers)
            odds_agg = odds_data.groupby('match_id').agg({
                'home_win_odds': 'mean',
                'draw_odds': 'mean',
                'away_win_odds': 'mean'
            }).reset_index()
            
            integrated = integrated.merge(odds_agg, on='match_id', how='left')
        
        # Integrate weather data if available
        if not weather_data.empty and 'match_id' in weather_data.columns:
            weather_cols = ['temperature_c', 'precipitation_mm', 'wind_kph', 'humidity', 'condition']
            available_cols = [col for col in weather_cols if col in weather_data.columns]
            
            if available_cols:
                weather_subset = weather_data[['match_id'] + available_cols]
                integrated = integrated.merge(weather_subset, on='match_id', how='left')
        
        # Fill missing values with sensible defaults
        integrated = self._fill_missing_values(integrated)
        
        return integrated
    
    def _fill_missing_values(self, df):
        """Fill missing values with sensible defaults"""
        # Fill numeric columns with appropriate values
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            # Skip ID columns
            if 'id' in col.lower():
                continue
                
            # Fill with column mean
            df[col] = df[col].fillna(df[col].mean())
        
        # Fill categorical columns with mode
        cat_cols = df.select_dtypes(include=['object']).columns
        for col in cat_cols:
            # Skip ID and name columns
            if 'id' in col.lower() or 'name' in col.lower() or 'team' in col.lower():
                continue
                
            # Fill with most common value
            if not df[col].empty:
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else '')
        
        return df
    
    def _load_integrated_data(self, df):
        """Load integrated data to database"""
        logger.info(f"Loading {len(df)} records to database")
        
        try:
            # Save to integrated_matches table
            df.to_sql('integrated_matches', self.db_engine, if_exists='replace', index=False)
            logger.info("Data loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading data to database: {str(e)}")
            return False