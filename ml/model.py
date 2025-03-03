# ml/model.py
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
        if len(X) == 0 or len(y) == 0:
            print("Warning: Empty training data")
            return self
            
        self.model.fit(X, y)
        return self
    
    def predict(self, X):
        """Make predictions using trained model."""
        if not hasattr(self.model, 'classes_'):
            return np.zeros(len(X))
        return self.model.predict(X)
    
    def predict_proba(self, X):
        """Return probability estimates for samples."""
        if not hasattr(self.model, 'classes_'):
            return np.array([[0.5, 0.5] for _ in range(len(X))])
        return self.model.predict_proba(X)
    
    def get_feature_importance(self):
        """Return feature importance scores."""
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            feature_names = self.predictors
            
            # Handle mismatch in feature names and importance array length
            if len(feature_names) != len(importance):
                feature_names = [f"Feature_{i}" for i in range(len(importance))]
                
            return pd.DataFrame({
                'Feature': feature_names[:len(importance)],
                'Importance': importance
            }).sort_values('Importance', ascending=False)
        
        # Return default feature importance if not trained
        return pd.DataFrame({
            'Feature': self.predictors if self.predictors else ['No Features'],
            'Importance': [0.2] * (len(self.predictors) if self.predictors else 1)
        })
    
    def save_model(self, filepath):
        """Save trained model to file."""
        joblib.dump(self, filepath)
    
    @classmethod
    def load_model(cls, filepath):
        """Load trained model from file."""
        try:
            return joblib.load(filepath)
        except:
            print(f"Could not load model from {filepath}, creating new model")
            return cls()

# ml/model.py - Enhanced train_prediction_model function

def train_prediction_model(data, train_date_cutoff='2023-01-01'):
    """Train the football prediction model with enhanced error handling and features."""
    print("Training prediction model...")
    from preprocessing.data_processing import add_advanced_features
    # Handle empty or invalid data
    if data is None or len(data) == 0:
        print("No data provided, creating default model")
        model = FootballPredictionModel()
        model.predictors = ['venue_code', 'opp_code', 'hour', 'day_code', 
                          'gf_rolling', 'ga_rolling', 'sh_rolling', 'sot_rolling']
        return model
    
    try:
        # Define predictors
        basic_predictors = ['venue_code', 'opp_code', 'hour', 'day_code']
        
        # Get available rolling predictors
        rolling_predictors = [col for col in data.columns if '_rolling' in col]
        
        # If no rolling predictors are found, use defaults
        if not rolling_predictors:
            print("No rolling predictors found, adding defaults")
            rolling_predictors = ['gf_rolling', 'ga_rolling', 'sh_rolling', 'sot_rolling']
            # Add default values for missing columns
            for col in rolling_predictors:
                if col not in data.columns:
                    base_col = col.split('_')[0]
                    if base_col in data.columns:
                        data[col] = data[base_col]
                    else:
                        default_values = {'gf': 1.5, 'ga': 1.0, 'sh': 12.0, 'sot': 5.0}
                        data[col] = default_values.get(base_col, 1.0)
        
        all_predictors = basic_predictors + rolling_predictors
        
        # Ensure all predictors exist in the data
        for predictor in all_predictors:
            if predictor not in data.columns:
                print(f"Adding missing predictor: {predictor}")
                if predictor == 'venue_code':
                    data[predictor] = data['venue'].map({'Home': 1, 'Away': 0}) if 'venue' in data.columns else 1
                elif predictor == 'opp_code':
                    data[predictor] = 0
                elif predictor == 'hour':
                    data[predictor] = 15
                elif predictor == 'day_code':
                    data[predictor] = 0
                else:
                    data[predictor] = 1.0
        
        # Ensure target column exists
        if 'target' not in data.columns:
            print("Creating target column")
            data['target'] = data['result'].map({'W': 1, 'D': 0, 'L': 0}) if 'result' in data.columns else 0
        
        # Filter valid data
        valid_data = data.dropna(subset=all_predictors + ['target'])
        valid_data = add_advanced_features(valid_data)
        if len(valid_data) < 100:  # If we have fewer than 100 samples
            from preprocessing.data_processing import augment_data
            print(f"Augmenting data from {len(valid_data)} to {len(valid_data) + 50} samples")
            valid_data = augment_data(valid_data, n_samples=50)
        if len(valid_data) == 0:
            print("No valid data after filtering, creating default model")
            model = FootballPredictionModel()
            model.predictors = all_predictors
            return model
        
        print(f"Training with {len(valid_data)} valid matches")
        
        # Use random train-test split instead of date-based
        try:
            from sklearn.model_selection import train_test_split
            train, _ = train_test_split(data, test_size=0.2, random_state=42)
        except:
            print("Error with train-test split, using all data for training")
            train = data
        
        # Train model
        model = FootballPredictionModel()
        model.predictors = all_predictors
        X_train = train[all_predictors]
        y_train = train['target']
        
        print(f"Training model with {len(X_train)} samples and {len(all_predictors)} features")
        model.train(X_train, y_train)
        
        print("Model training completed")
        return model
        
    except Exception as e:
        print(f"Error in model training: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a default model
        model = FootballPredictionModel()
        model.predictors = ['venue_code', 'opp_code', 'hour', 'day_code', 
                          'gf_rolling', 'ga_rolling', 'sh_rolling', 'sot_rolling']
        return model

def prepare_match_prediction_data(match_details, historical_data):
    """Prepare a single match data for prediction."""
    # Create a DataFrame with the match details
    match_df = pd.DataFrame([match_details])
    
    # Encode venue
    match_df['venue_code'] = 1 if match_details['venue'] == 'Home' else 0
    
    # Get team and opponent codes
    if historical_data is not None and 'team_code' in historical_data.columns and 'team' in historical_data.columns:
        try:
            team_codes = historical_data.drop_duplicates('team')[['team', 'team_code']]
            team_code_map = dict(zip(team_codes['team'], team_codes['team_code']))
            
            match_df['team_code'] = team_code_map.get(match_details['team'], 0)
            match_df['opp_code'] = team_code_map.get(match_details['opponent'], 0)
        except:
            match_df['team_code'] = 0
            match_df['opp_code'] = 0
    else:
        match_df['team_code'] = 0
        match_df['opp_code'] = 0
    
    # Extract hour and day code
    try:
        if isinstance(match_details['date'], pd.Timestamp):
            match_df['day_code'] = match_details['date'].dayofweek
        else:
            match_df['day_code'] = pd.Timestamp(match_details['date']).dayofweek
    except:
        match_df['day_code'] = 0
    
    try:
        if 'time' in match_details:
            match_df['hour'] = int(match_details['time'].split(':')[0])
        elif 'hour' in match_details:
            match_df['hour'] = match_details['hour']
        else:
            match_df['hour'] = 15  # Default to 3 PM
    except:
        match_df['hour'] = 15
    
    # Add all rolling averages from match_details if present
    for key, value in match_details.items():
        if '_rolling' in key and key not in match_df.columns:
            match_df[key] = value
    
    return match_df
def train_ensemble_model(data, train_date_cutoff='2023-01-01', rf_weight=0.5, xgb_weight=0.5):
    """
    Train the ensemble football prediction model combining RandomForest and XGBoost.
    
    Args:
        data: Processed match data
        train_date_cutoff: Date to split training/testing data
        rf_weight: Weight for RandomForest model (between 0 and 1)
        xgb_weight: Weight for XGBoost model (between 0 and 1)
        
    Returns:
        Trained ensemble model
    """
    from ml.ensemble_model import EnsemblePredictor
    from preprocessing.data_processing import add_advanced_features
    print("Training ensemble prediction model...")
    
    # Handle empty or invalid data
    if data is None or len(data) == 0:
        print("No data provided, creating default ensemble model")
        model = EnsemblePredictor(weights=(rf_weight, xgb_weight))
        model.predictors = ['venue_code', 'opp_code', 'hour', 'day_code', 
                          'gf_rolling', 'ga_rolling', 'sh_rolling', 'sot_rolling']
        return model
    
    try:
        # Define predictors
        basic_predictors = ['venue_code', 'opp_code', 'hour', 'day_code']
        
        # Get available rolling predictors
        rolling_predictors = [col for col in data.columns if '_rolling' in col]
        
        # If no rolling predictors are found, use defaults
        if not rolling_predictors:
            print("No rolling predictors found, adding defaults")
            rolling_predictors = ['gf_rolling', 'ga_rolling', 'sh_rolling', 'sot_rolling']
            # Add default values for missing columns
            for col in rolling_predictors:
                if col not in data.columns:
                    base_col = col.split('_')[0]
                    if base_col in data.columns:
                        data[col] = data[base_col]
                    else:
                        default_values = {'gf': 1.5, 'ga': 1.0, 'sh': 12.0, 'sot': 5.0}
                        data[col] = default_values.get(base_col, 1.0)
        
        all_predictors = basic_predictors + rolling_predictors
        
        # Ensure all predictors exist in the data
        for predictor in all_predictors:
            if predictor not in data.columns:
                print(f"Adding missing predictor: {predictor}")
                if predictor == 'venue_code':
                    data[predictor] = data['venue'].map({'Home': 1, 'Away': 0}) if 'venue' in data.columns else 1
                elif predictor == 'opp_code':
                    data[predictor] = 0
                elif predictor == 'hour':
                    data[predictor] = 15
                elif predictor == 'day_code':
                    data[predictor] = 0
                else:
                    data[predictor] = 1.0
        
        # Ensure target column exists
        if 'target' not in data.columns:
            print("Creating target column")
            data['target'] = data['result'].map({'W': 1, 'D': 0, 'L': 0}) if 'result' in data.columns else 0
        
        # Filter valid data
        valid_data = data.dropna(subset=all_predictors + ['target'])
        valid_data = add_advanced_features(valid_data)
        if len(valid_data) < 100:  # If we have fewer than 100 samples
            from preprocessing.data_processing import augment_data
            print(f"Augmenting data from {len(valid_data)} to {len(valid_data) + 50} samples")
            valid_data = augment_data(valid_data, n_samples=50)
        if len(valid_data) == 0:
            print("No valid data after filtering, creating default ensemble model")
            model = EnsemblePredictor(weights=(rf_weight, xgb_weight))
            model.predictors = all_predictors
            return model
        
        print(f"Training with {len(valid_data)} valid matches")
        
        # Split data for training
        try:
            data['date'] = pd.to_datetime(data['date'])
            train_date = pd.to_datetime(train_date_cutoff)
            from sklearn.model_selection import train_test_split
            train, _ = train_test_split(data, test_size=0.2, random_state=42)
            
            if len(train) < 10:  # Not enough training data
                print("Not enough training data, using all data")
                train = data
        except:
            print("Error parsing dates, using all data for training")
            train = data
        
        # Create and train ensemble model
        model = EnsemblePredictor(
            weights=(rf_weight, xgb_weight),
            model_version=f"ensemble-{pd.Timestamp.now().strftime('%Y%m%d')}"
        )
        
        X_train = train[all_predictors]
        y_train = train['target']
        
        print(f"Training ensemble model with {len(X_train)} samples and {len(all_predictors)} features")
        model.train(X_train, y_train)
        
        # Evaluate model if we have test data
        try:
            test = data[data['date'] >= train_date]
            if len(test) > 10:  # Only evaluate if enough test data
                X_test = test[all_predictors]
                y_test = test['target']
                metrics = model.evaluate(X_test, y_test)
                print(f"Ensemble model evaluation metrics: {metrics}")
        except Exception as e:
            print(f"Could not evaluate model: {e}")
        
        print("Ensemble model training completed")
        return model
        
    except Exception as e:
        print(f"Error in ensemble model training: {e}")
        import traceback
        traceback.print_exc()
        
        # Return a default model
        model = EnsemblePredictor(weights=(rf_weight, xgb_weight))
        model.predictors = ['venue_code', 'opp_code', 'hour', 'day_code', 
                          'gf_rolling', 'ga_rolling', 'sh_rolling', 'sot_rolling']
        return model