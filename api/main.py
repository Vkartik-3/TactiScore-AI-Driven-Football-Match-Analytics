# api/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Add this import
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import io
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing.data_processing import load_data, prepare_model_data
from ml.model import train_prediction_model, prepare_match_prediction_data

app = FastAPI(title="Football Prediction API")

# Add CORS middleware - add this code block
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models for API requests and responses
class MatchPredictionRequest(BaseModel):
    home_team: str
    away_team: str
    match_date: str
    match_time: str
    team_to_predict: str  # "home" or "away"
    # Form stats
    goals_for: float
    goals_against: float
    shots: float
    shots_on_target: float
    # Optional additional stats
    distance: Optional[float] = None
    free_kicks: Optional[float] = None
    penalties: Optional[float] = None
    penalty_attempts: Optional[float] = None

class PredictionResponse(BaseModel):
    team: str
    opponent: str
    win_probability: float
    prediction: str
    key_factors: List[dict]

# Load data and model
MODEL_PATH = "../models/trained_model.pkl"
DATA_PATH = "data/test_matches.csv"

@app.on_event("startup")
async def startup_event():
    try:
        # Try to load existing data
        app.state.data = load_data(DATA_PATH)
        app.state.processed_data = prepare_model_data(app.state.data) if not app.state.data.empty else None
        app.state.model = train_prediction_model(app.state.processed_data) if app.state.processed_data is not None else None
    except Exception as e:
        print(f"Error during startup: {e}")
        # Initialize with empty data
        app.state.data = pd.DataFrame(columns=['date', 'team', 'opponent', 'venue', 'result', 'gf', 'ga', 'sh', 'sot'])
        app.state.processed_data = None
        app.state.model = None

@app.get("/")
async def root():
    return {"message": "Football Prediction System API"}

@app.get("/teams/")
async def get_teams():
    """Return list of teams in the dataset"""
    if app.state.data is None or app.state.data.empty:
        return []
    
    teams = app.state.data['team'].unique().tolist() if 'team' in app.state.data.columns else []
    return sorted(teams)

@app.get("/team-stats/{team_name}")
async def get_team_stats(team_name: str):
    """Return statistics for a specific team"""
    if app.state.data is None or app.state.data.empty:
        raise HTTPException(status_code=404, detail="No data available. Please upload data first.")
    
    if 'team' not in app.state.data.columns or team_name not in app.state.data['team'].values:
        raise HTTPException(status_code=404, detail=f"Team {team_name} not found in data")
    
    team_data = app.state.data[app.state.data['team'] == team_name]
    
    # Calculate basic stats
    matches = team_data.to_dict('records')
    
    # Create summary stats
    wins = sum(1 for match in matches if match.get('result') == 'W')
    draws = sum(1 for match in matches if match.get('result') == 'D')
    losses = sum(1 for match in matches if match.get('result') == 'L')
    
    return {
        "matches": matches,
        "stats": {
            "matches_played": len(matches),
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "win_percentage": round(wins / len(matches) * 100, 1) if matches else 0
        }
    }

@app.get("/head-to-head/{team1}/{team2}")
async def get_head_to_head(team1: str, team2: str):
    """Return head to head statistics between two teams"""
    if app.state.data is None or app.state.data.empty:
        raise HTTPException(status_code=404, detail="No data available. Please upload data first.")
    
    # Sample data structure since we can't compute real head-to-head stats without more data
    return {
        "stats": {
            "team1": {"attack": 75, "defense": 70, "possession": 65, "form": 80, "homeAdvantage": 75},
            "team2": {"attack": 65, "defense": 75, "possession": 60, "form": 70, "awayPerformance": 60}
        },
        "history": []  # This would contain previous match results
    }

@app.get("/data-insights/")
async def get_data_insights():
    """Return insights from the uploaded data"""
    if app.state.data is None or app.state.data.empty:
        raise HTTPException(status_code=404, detail="No data available. Please upload data first.")
    
    # Create dummy insights structure
    result_counts = app.state.data['result'].value_counts().to_dict() if 'result' in app.state.data.columns else {'W': 0, 'D': 0, 'L': 0}
    total_matches = sum(result_counts.values())
    
    # Calculate percentages
    result_distribution = [
        {"name": "Win", "value": round(result_counts.get('W', 0) / total_matches * 100, 1) if total_matches else 0},
        {"name": "Draw", "value": round(result_counts.get('D', 0) / total_matches * 100, 1) if total_matches else 0},
        {"name": "Loss", "value": round(result_counts.get('L', 0) / total_matches * 100, 1) if total_matches else 0}
    ]
    
    return {
        "resultDistribution": result_distribution,
        "venueAnalysis": {
            "Home": {"Win": 60, "Draw": 20, "Loss": 20},
            "Away": {"Win": 30, "Draw": 30, "Loss": 40}
        },
        "teamPerformance": {
            team: {"Win": 60, "Draw": 20, "Loss": 20, "WinPercent": 60}
            for team in app.state.data['team'].unique().tolist() if 'team' in app.state.data.columns
        },
        "statsCorrelation": [
            {"stat": "Shots on Target", "correlation": 0.75},
            {"stat": "Goals For", "correlation": 0.72},
            {"stat": "Possession", "correlation": 0.58},
            {"stat": "Distance", "correlation": -0.32},
            {"stat": "Goals Against", "correlation": -0.65}
        ]
    }
@app.post("/predict/", response_model=PredictionResponse)
async def predict_match(prediction_request: MatchPredictionRequest):
    if app.state.model is None:
        raise HTTPException(status_code=404, detail="No model available. Please upload data first to train the model.")
    # Determine which team to predict for
    if prediction_request.team_to_predict.lower() == "home":
        team = prediction_request.home_team
        opponent = prediction_request.away_team
        venue = "Home"
    else:
        team = prediction_request.away_team
        opponent = prediction_request.home_team
        venue = "Away"
    
    # Create match details dictionary
    match_details = {
        "date": prediction_request.match_date,
        "time": prediction_request.match_time,
        "team": team,
        "opponent": opponent,
        "venue": venue,
        "gf_rolling": prediction_request.goals_for,
        "ga_rolling": prediction_request.goals_against,
        "sh_rolling": prediction_request.shots,
        "sot_rolling": prediction_request.shots_on_target,
    }
    
    # Add optional stats if provided
    if prediction_request.distance:
        match_details["dist_rolling"] = prediction_request.distance
    if prediction_request.free_kicks:
        match_details["fk_rolling"] = prediction_request.free_kicks
    if prediction_request.penalties:
        match_details["pk_rolling"] = prediction_request.penalties
    if prediction_request.penalty_attempts:
        match_details["pkatt_rolling"] = prediction_request.penalty_attempts
    
    # Prepare data for prediction
    match_df = prepare_match_prediction_data(match_details, app.state.processed_data)
    
    # Extract features used in training
    predictors = app.state.model.predictors
    available_predictors = [p for p in predictors if p in match_df.columns]
    
    # Make prediction
    win_probability = app.state.model.predict_proba(match_df[available_predictors])[0][1]
    prediction = "WIN" if win_probability > 0.5 else "NOT WIN"
    
    # Get feature importance
    feature_importance = app.state.model.get_feature_importance()
    key_factors = feature_importance.head(5).to_dict('records')
    
    return {
        "team": team,
        "opponent": opponent,
        "win_probability": float(win_probability),
        "prediction": prediction,
        "key_factors": key_factors
    }

@app.post("/upload-data/")
async def upload_data(file: UploadFile = File(...)):
    # Check if file is CSV
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Read file content
    contents = await file.read()
    
    try:
        # Parse CSV
        data = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Process data
        processed_data = prepare_model_data(data)
        
        # Update application state
        app.state.data = data
        app.state.processed_data = processed_data
        app.state.model = train_prediction_model(processed_data)
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        
        # Save data to file
        data.to_csv(DATA_PATH, index=False)
        
        return {"filename": file.filename, "rows": len(data), "columns": len(data.columns)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")