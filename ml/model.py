from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import pickle
import joblib
import numpy as np

class FootballPredictionModel:
    def __init__(self, n_estimators=200, min_samples_split=10):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            min_samples_split=min_samples_split,
            random_state=1
        )
        self.predictors = []
        
    def train(self, X, y):
        """Train the model with provided features and target."""
        self.model.fit(X, y)
        return self
    
    def predict(self, X):
        """Make predictions using trained model."""
        return self.model.predict(X)
    
    def predict_proba(self, X):
        """Return probability estimates for samples."""
        return self.model.predict_proba(X)
    
    def get_feature_importance(self):
        """Return feature importance scores."""
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            feature_names = self.predictors
            return pd.DataFrame({
                'Feature': feature_names,
                'Importance': importance
            }).sort_values('Importance', ascending=False)
        return None
    
    def save_model(self, filepath):
        """Save trained model to file."""
        joblib.dump(self, filepath)
    
    @classmethod
    def load_model(cls, filepath):
        """Load trained model from file."""
        return joblib.load(filepath)

def train_prediction_model(data, train_date_cutoff='2022-01-01'):
    """Train the football prediction model."""
    # Define predictors
    basic_predictors = ['venue_code', 'opp_code', 'hour', 'day_code']
    rolling_predictors = [col for col in data.columns if '_rolling' in col]
    all_predictors = basic_predictors + rolling_predictors
    
    # Split data
    train = data[data['date'] < train_date_cutoff]
    
    # Train model
    model = FootballPredictionModel()
    model.predictors = all_predictors
    X_train = train[all_predictors]
    y_train = train['target']
    model.train(X_train, y_train)
    
    return model

def prepare_match_prediction_data(match_details, historical_data):
    """Prepare a single match data for prediction."""
    # Create a DataFrame with the match details
    match_df = pd.DataFrame([match_details])
    
    # Encode venue
    match_df['venue_code'] = 1 if match_details['venue'] == 'Home' else 0
    
    # Get team and opponent codes
    team_codes = historical_data.drop_duplicates('team')[['team', 'team_code']]
    team_code_map = dict(zip(team_codes['team'], team_codes['team_code']))
    
    match_df['team_code'] = team_code_map.get(match_details['team'], 0)
    match_df['opp_code'] = team_code_map.get(match_details['opponent'], 0)
    
    # Extract hour and day code
    if isinstance(match_details['date'], pd.Timestamp):
        match_df['day_code'] = match_details['date'].dayofweek
    else:
        match_df['day_code'] = pd.Timestamp(match_details['date']).dayofweek
    
    match_df['hour'] = int(match_details['time'].split(':')[0])
    
    return match_df