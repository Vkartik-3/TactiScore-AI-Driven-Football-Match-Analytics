# data_pipeline/processors/feature_generator.py
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureGenerator:
    def __init__(self):
        self.window_sizes = [3, 5, 10]
        self.standard_team_names = None  # Will load from database
    
    def generate_features(self, df):
        """
        Generate advanced features from raw match data.
        
        Args:
            df: DataFrame with match data
        
        Returns:
            DataFrame with additional features
        """
        logger.info("Generating features from match data")
        
        if df.empty:
            logger.warning("Empty dataframe provided, returning empty features")
            return pd.DataFrame()
            
        # Make a copy to avoid modifying the original
        features = df.copy()
        
        # Ensure required columns exist
        required_cols = ['team', 'opponent', 'date', 'venue', 'result', 'goals_for', 'goals_against']
        missing_cols = [col for col in required_cols if col not in features.columns]
        
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Sort by team and date
        features = features.sort_values(['team', 'date'])
        
        # Add binary flags
        features['is_win'] = (features['result'] == 'W').astype(int)
        features['is_draw'] = (features['result'] == 'D').astype(int)
        features['is_loss'] = (features['result'] == 'L').astype(int)
        features['clean_sheet'] = (features['goals_against'] == 0).astype(int)
        features['failed_to_score'] = (features['goals_for'] == 0).astype(int)
        features['points'] = features['result'].map({'W': 3, 'D': 1, 'L': 0})
        
        # Generate team form features
        features = self._add_team_form_features(features)
        
        # Generate venue-specific features
        features = self._add_venue_features(features)
        
        # Add head-to-head features if data available
        features = self._add_head_to_head_features(features)
        
        # Add betting odds features if available
        if {'home_win_odds', 'draw_odds', 'away_win_odds'}.issubset(features.columns):
            features = self._add_odds_features(features)
        
        # Add weather impact features if available
        if {'temperature_c', 'precipitation_mm', 'wind_kph'}.issubset(features.columns):
            features = self._add_weather_features(features)
        
        # Add fixture congestion features
        features = self._add_schedule_features(features)
        
        logger.info(f"Generated {len(features.columns) - len(df.columns)} new features")
        return features
    
    def _add_team_form_features(self, df):
        """Add rolling window statistics for team form"""
        logger.info("Adding team form features")
        
        for window in self.window_sizes:
            # Points in last N matches
            df[f'points_last_{window}'] = df.groupby('team')['points'].transform(
                lambda x: x.rolling(window, min_periods=1).sum()
            )
            
            # Goals scored in last N matches
            df[f'goals_for_last_{window}'] = df.groupby('team')['goals_for'].transform(
                lambda x: x.rolling(window, min_periods=1).sum()
            )
            
            # Goals conceded in last N matches
            df[f'goals_against_last_{window}'] = df.groupby('team')['goals_against'].transform(
                lambda x: x.rolling(window, min_periods=1).sum()
            )
            
            # Win rate in last N matches
            df[f'win_rate_last_{window}'] = df.groupby('team')['is_win'].transform(
                lambda x: x.rolling(window, min_periods=1).mean()
            )
            
            # Goal difference in last N matches
            df[f'goal_diff_last_{window}'] = df[f'goals_for_last_{window}'] - df[f'goals_against_last_{window}']
            
            # Clean sheets in last N matches
            df[f'clean_sheets_last_{window}'] = df.groupby('team')['clean_sheet'].transform(
                lambda x: x.rolling(window, min_periods=1).sum()
            )
            
            # Failed to score in last N matches
            df[f'failed_to_score_last_{window}'] = df.groupby('team')['failed_to_score'].transform(
                lambda x: x.rolling(window, min_periods=1).sum()
            )
        
        # Calculate momentum (trend in recent performance)
        if len(self.window_sizes) >= 2:
            small_window = min(self.window_sizes)
            large_window = max(self.window_sizes)
            
            df['points_momentum'] = df[f'points_last_{small_window}'] / small_window - df[f'points_last_{large_window}'] / large_window
            df['goals_momentum'] = df[f'goals_for_last_{small_window}'] / small_window - df[f'goals_for_last_{large_window}'] / large_window
        
        return df
    
    def _add_venue_features(self, df):
        """Add home/away specific performance metrics"""
        logger.info("Adding venue-specific features")
        
        # Process home form
        home_df = df[df['venue'] == 'Home'].copy()
        home_metrics = home_df.groupby('team').agg({
            'points': 'mean',
            'goals_for': 'mean',
            'goals_against': 'mean',
            'is_win': 'mean'
        }).rename(columns={
            'points': 'home_points_avg',
            'goals_for': 'home_goals_for_avg',
            'goals_against': 'home_goals_against_avg',
            'is_win': 'home_win_rate'
        })
        
        # Process away form
        away_df = df[df['venue'] == 'Away'].copy()
        away_metrics = away_df.groupby('team').agg({
            'points': 'mean',
            'goals_for': 'mean',
            'goals_against': 'mean',
            'is_win': 'mean'
        }).rename(columns={
            'points': 'away_points_avg',
            'goals_for': 'away_goals_for_avg',
            'goals_against': 'away_goals_against_avg',
            'is_win': 'away_win_rate'
        })
        
        # Merge home and away metrics back to main dataframe
        result = df.merge(home_metrics, left_on='team', right_index=True, how='left')
        result = result.merge(away_metrics, left_on='team', right_index=True, how='left')
        
        # Add home advantage metrics
        result['home_advantage'] = result['home_points_avg'] - result['away_points_avg']
        
        return result
    
    def _add_head_to_head_features(self, df):
        """Add head-to-head statistics between teams"""
        logger.info("Adding head-to-head features")
        
        # Group by team pairs and compute statistics
        h2h_results = []
        
        teams = df['team'].unique()
        for team in teams:
            for opponent in teams:
                if team != opponent:
                    # Get matches between these teams
                    team_matches = df[(df['team'] == team) & (df['opponent'] == opponent)]
                    
                    if len(team_matches) > 0:
                        # Calculate h2h stats
                        h2h_stats = {
                            'team': team,
                            'opponent': opponent,
                            'h2h_matches': len(team_matches),
                            'h2h_wins': sum(team_matches['result'] == 'W'),
                            'h2h_draws': sum(team_matches['result'] == 'D'),
                            'h2h_losses': sum(team_matches['result'] == 'L'),
                            'h2h_goals_for': team_matches['goals_for'].sum(),
                            'h2h_goals_against': team_matches['goals_against'].sum()
                        }
                        
                        # Calculate derived metrics
                        if h2h_stats['h2h_matches'] > 0:
                            h2h_stats['h2h_win_rate'] = h2h_stats['h2h_wins'] / h2h_stats['h2h_matches']
                            h2h_stats['h2h_points_per_game'] = (h2h_stats['h2h_wins'] * 3 + h2h_stats['h2h_draws']) / h2h_stats['h2h_matches']
                            h2h_stats['h2h_avg_goals_for'] = h2h_stats['h2h_goals_for'] / h2h_stats['h2h_matches']
                            h2h_stats['h2h_avg_goals_against'] = h2h_stats['h2h_goals_against'] / h2h_stats['h2h_matches']
                        
                        h2h_results.append(h2h_stats)
        
        if h2h_results:
            h2h_df = pd.DataFrame(h2h_results)
            result = df.merge(h2h_df, on=['team', 'opponent'], how='left')
            
            # Fill NAs with sensible defaults
            for col in [c for c in result.columns if c.startswith('h2h_')]:
                if col.endswith('_rate') or col.endswith('_per_game'):
                    result[col] = result[col].fillna(0.5)  # Neutral expectation
                elif col.endswith('_matches'):
                    result[col] = result[col].fillna(0)
                else:
                    result[col] = result[col].fillna(0)
                    
            return result
        
        return df
    
    def _add_odds_features(self, df):
        """Add betting market derived features"""
        logger.info("Adding betting odds features")
        
        # Convert odds to probabilities
        df['implied_home_win_prob'] = 1 / df['home_win_odds']
        df['implied_draw_prob'] = 1 / df['draw_odds']
        df['implied_away_win_prob'] = 1 / df['away_win_odds']
        
        # Normalize to account for overround
        prob_columns = ['implied_home_win_prob', 'implied_draw_prob', 'implied_away_win_prob']
        df['total_implied_prob'] = df[prob_columns].sum(axis=1)
        
        for col in prob_columns:
            df[f"{col}_normalized"] = df[col] / df['total_implied_prob']
        
        # Add market-derived features
        df['market_expected_goals'] = df.apply(
            lambda row: 1.5 * row['implied_home_win_prob_normalized'] + 
                        0.9 * row['implied_draw_prob_normalized'] + 
                        0.6 * row['implied_away_win_prob_normalized'],
            axis=1
        )
        
        # Add surprise factors (actual vs expected)
        df['win_surprise'] = df['is_win'] - df.apply(
            lambda row: row['implied_home_win_prob_normalized'] if row['venue'] == 'Home' 
                        else row['implied_away_win_prob_normalized'],
            axis=1
        )
        
        return df
    
    def _add_weather_features(self, df):
        """Add weather-related performance features"""
        logger.info("Adding weather impact features")
        
        # Create weather condition categories
        df['is_rainy'] = df['precipitation_mm'] > 1.0
        df['is_windy'] = df['wind_kph'] > 25.0
        df['is_cold'] = df['temperature_c'] < 5.0
        df['is_hot'] = df['temperature_c'] > 25.0
        
        # Calculate team performance in different weather conditions
        for condition in ['is_rainy', 'is_windy', 'is_cold', 'is_hot']:
            # Home performance in this condition
            home_perf = df[df['venue'] == 'Home'].groupby(['team', condition])['points'].mean().unstack()
            home_perf.columns = [f'home_points_normal', f'home_points_{condition[3:]}']
            
            # Away performance in this condition
            away_perf = df[df['venue'] == 'Away'].groupby(['team', condition])['points'].mean().unstack()
            away_perf.columns = [f'away_points_normal', f'away_points_{condition[3:]}']
            
            # Combine and calculate weather impact
            weather_impact = pd.DataFrame(index=df['team'].unique())
            
            if not home_perf.empty and set(['home_points_normal', f'home_points_{condition[3:]}']).issubset(home_perf.columns):
                weather_impact[f'home_{condition[3:]}_impact'] = home_perf[f'home_points_{condition[3:]}'] - home_perf['home_points_normal']
                
            if not away_perf.empty and set(['away_points_normal', f'away_points_{condition[3:]}']).issubset(away_perf.columns):
                weather_impact[f'away_{condition[3:]}_impact'] = away_perf[f'away_points_{condition[3:]}'] - away_perf['away_points_normal']
            
            # Merge weather impact features
            if not weather_impact.empty:
                df = df.merge(weather_impact, left_on='team', right_index=True, how='left')
        
        return df
    
    def _add_schedule_features(self, df):
        """Add features related to fixture congestion and rest days"""
        logger.info("Adding schedule-related features")
        
        # Sort by team and date
        df = df.sort_values(['team', 'date'])
        
        # Calculate days since last match
        df['prev_match_date'] = df.groupby('team')['date'].shift(1)
        df['days_since_last_match'] = (df['date'] - df['prev_match_date']).dt.days
        
        # Calculate match density (matches in last 30 days)
        def count_matches_in_last_n_days(dates, current_idx, n_days=30):
            current_date = dates.iloc[current_idx]
            prior_dates = dates.iloc[:current_idx]
            return sum((current_date - prior_dates).dt.days <= n_days)
        
        df['match_density_30d'] = df.groupby('team')['date'].transform(
            lambda dates: [count_matches_in_last_n_days(dates, i) for i in range(len(dates))]
        )
        
        # Flag for quick turnaround (less than 4 days since last match)
        df['quick_turnaround'] = (df['days_since_last_match'] < 4) & (df['days_since_last_match'].notna())
        
        # Historical performance based on rest days
        rest_perf = df.groupby(['team', pd.cut(df['days_since_last_match'], bins=[0, 3, 6, float('inf')], labels=['short', 'medium', 'long'])])['points'].mean()
        if not rest_perf.empty:
            rest_perf = rest_perf.unstack().fillna(rest_perf.mean())
            rest_perf.columns = ['points_short_rest', 'points_medium_rest', 'points_long_rest']
            
            # Merge rest performance
            df = df.merge(rest_perf, left_on='team', right_index=True, how='left')
        
        return df