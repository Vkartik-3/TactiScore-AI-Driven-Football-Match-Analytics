import pandas as pd
import numpy as np

def load_data(file_path):
    """Load and preprocess the football match data."""
    try:
        matches = pd.read_csv(file_path, index_col=0)
        
        # Check if essential columns exist, if not create empty DataFrame with required columns
        required_columns = ['date', 'team', 'opponent', 'venue', 'result', 'gf', 'ga', 'sh', 'sot']
        
        if not all(col in matches.columns for col in required_columns):
            # Create empty DataFrame with required columns
            matches = pd.DataFrame(columns=required_columns)
            
        # Ensure date is datetime
        if 'date' in matches.columns:
            matches['date'] = pd.to_datetime(matches['date'])
            
        return matches
    except FileNotFoundError:
        # Create and return empty DataFrame with required columns
        return pd.DataFrame(columns=['date', 'team', 'opponent', 'venue', 'result', 'gf', 'ga', 'sh', 'sot'])

def encode_categorical_features(df):
    """Convert categorical variables to numerical codes."""
    df['venue_code'] = df['venue'].astype('category').cat.codes
    df['opp_code'] = df['opponent'].astype('category').cat.codes
    df['hour'] = df['time'].str.replace(':.+', '', regex=True).astype('int')
    df['day_code'] = df['date'].dt.dayofweek
    df['target'] = (df['result'] == 'W').astype('int')
    return df

def calculate_rolling_averages(group, cols, new_cols):
    """Calculate rolling averages for key metrics."""
    group = group.sort_values('date')
    rolling_stats = group[cols].rolling(3, closed='left').mean()
    group[new_cols] = rolling_stats
    group = group.dropna(subset=new_cols)
    return group

def prepare_model_data(df):
    """Prepare data for model training with all preprocessing steps."""
    # Apply initial encoding
    df = encode_categorical_features(df)
    
    # Calculate rolling averages
    cols = ['gf', 'ga', 'sh', 'sot', 'dist', 'fk', 'pk', 'pkatt']
    new_cols = [f"{c}_rolling" for c in cols]
    
    # Group by team and apply rolling averages
    matches_rolling = df.groupby('team').apply(
        lambda x: calculate_rolling_averages(x, cols, new_cols)
    )
    matches_rolling = matches_rolling.droplevel('team')
    matches_rolling.index = range(matches_rolling.shape[0])
    
    return matches_rolling