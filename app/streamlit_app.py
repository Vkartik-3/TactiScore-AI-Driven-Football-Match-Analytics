# app/streamlit_app.py
import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing.data_processing import load_data, prepare_model_data
from ml.model import train_prediction_model, prepare_match_prediction_data, FootballPredictionModel

# Set page config
st.set_page_config(
    page_title="Football Prediction System",
    page_icon="⚽",
    layout="wide"
)

# Title and description
st.title("⚽ Premier League Match Prediction System")
st.markdown("""
This application predicts the outcome of English Premier League matches based on historical data and team performance metrics.
Upload your match data CSV file to make predictions.
""")

# Sidebar for data uploading and model parameters
st.sidebar.header("Data Upload")

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload CSV file with match data", type="csv")

# Initialize data and model variables
data = None
processed_data = None
model = None
data_loaded = False

# Default data path
DEFAULT_DATA_PATH = "../data/matches.csv"
MODEL_PATH = "../models/trained_model.pkl"

# Try to load default data if no file is uploaded
if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
        st.sidebar.success("Data successfully loaded from upload!")
        data_loaded = True
    except Exception as e:
        st.sidebar.error(f"Error loading uploaded file: {e}")
else:
    try:
        data = load_data(DEFAULT_DATA_PATH)
        st.sidebar.info(f"Using default data from {DEFAULT_DATA_PATH}")
        data_loaded = True
    except Exception as e:
        st.sidebar.error(f"Could not load default data: {e}")

# Process data if loaded successfully
if data_loaded and data is not None:
    # Convert date to datetime if needed
    if 'date' in data.columns and not pd.api.types.is_datetime64_any_dtype(data['date']):
        data['date'] = pd.to_datetime(data['date'])
    
    # Process data
    processed_data = prepare_model_data(data)
    
    # Extract list of teams
    if 'team' in data.columns:
        teams_list = sorted(data['team'].unique().tolist())
        st.sidebar.info(f"Found {len(teams_list)} teams in the data")
    else:
        teams_list = []
        st.sidebar.warning("No team column found in data")

    # Model parameters
    st.sidebar.header("Model Parameters")
    n_estimators = st.sidebar.slider("Number of Trees", 50, 500, 200, 50)
    min_samples_split = st.sidebar.slider("Minimum Samples to Split", 2, 20, 10, 1)
    
    # Train model with parameters
    model = train_prediction_model(processed_data)

# Create tabs
if data_loaded:
    tab1, tab2, tab3 = st.tabs(["Make Prediction", "View Data", "Data Insights"])
    
    with tab1:
        st.header("Match Outcome Prediction")
        
        col1, col2 = st.columns(2)
        
        with col1:
            match_date = st.date_input("Match Date", date.today())
            match_time = st.time_input("Kickoff Time", datetime.strptime("15:00", "%H:%M").time())
            
            if teams_list:
                home_team = st.selectbox("Home Team", teams_list)
                away_options = [team for team in teams_list if team != home_team]
                away_team = st.selectbox("Away Team", away_options)
            else:
                home_team = st.text_input("Home Team")
                away_team = st.text_input("Away Team")
            
        with col2:
            team_to_predict = st.radio("Team to predict", ["Home Team", "Away Team"])
            venue = "Home" if team_to_predict == "Home Team" else "Away"
            team = home_team if team_to_predict == "Home Team" else away_team
            opponent = away_team if team_to_predict == "Home Team" else home_team
            
            st.subheader("Team Form Stats (Last 3 Games)")
            
            # Get team's recent stats if available
            recent_stats = {}
            if data is not None and 'team' in data.columns:
                team_data = data[data['team'] == team].sort_values('date', ascending=False)
                if len(team_data) >= 3:
                    for stat in ['gf', 'ga', 'sh', 'sot']:
                        if stat in team_data.columns:
                            recent_stats[stat] = team_data[stat].iloc[:3].mean()
            
            # Display form stats with recent values if available
            gf = st.number_input("Goals For (Avg)", 0.0, 5.0, recent_stats.get('gf', 1.5), 0.1)
            ga = st.number_input("Goals Against (Avg)", 0.0, 5.0, recent_stats.get('ga', 1.0), 0.1)
            sh = st.number_input("Shots (Avg)", 0.0, 30.0, recent_stats.get('sh', 12.0), 0.5)
            sot = st.number_input("Shots on Target (Avg)", 0.0, 15.0, recent_stats.get('sot', 5.0), 0.5)
        
        # Add additional stats section for metrics that may be in the CSV
        expander = st.expander("Additional Statistics (Optional)")
        with expander:
            additional_stats = {}
            for stat in ['dist', 'fk', 'pk', 'pkatt']:
                if data is not None and stat in data.columns:
                    team_avg = data[data['team'] == team][stat].mean() if len(data[data['team'] == team]) > 0 else 0
                    additional_stats[stat] = st.number_input(
                        f"{stat.upper()} (Avg)", 
                        0.0, 
                        50.0 if stat == 'dist' else 5.0, 
                        float(team_avg) if not np.isnan(team_avg) else (16.0 if stat == 'dist' else 1.0),
                        0.1
                    )
        
        # Create match details dict
        match_details = {
            'date': pd.Timestamp(match_date),
            'time': match_time.strftime("%H:%M"),
            'hour': match_time.hour,
            'team': team,
            'opponent': opponent,
            'venue': venue,
            'gf_rolling': gf,
            'ga_rolling': ga,
            'sh_rolling': sh,
            'sot_rolling': sot
        }
        
        # Add additional stats if available
        for stat, value in additional_stats.items():
            match_details[f"{stat}_rolling"] = value
        
        if st.button("Predict Match Outcome"):
            st.info("Making prediction based on provided details...")
            
            with st.spinner("Training model and making prediction..."):
                # Prepare data for prediction
                match_df = prepare_match_prediction_data(match_details, processed_data)
                
                # Extract features used in training
                predictors = model.predictors
                available_predictors = [p for p in predictors if p in match_df.columns]
                
                # Make prediction
                win_probability = model.predict_proba(match_df[available_predictors])[0][1]
                prediction = "WIN" if win_probability > 0.5 else "NOT WIN"
                
                # Get feature importance
                feature_importance = model.get_feature_importance()
                
                st.subheader("Prediction Results")
                
                # Display prediction
                if prediction == "WIN":
                    st.success(f"Prediction: {team} will WIN against {opponent}")
                else:
                    st.warning(f"Prediction: {team} will NOT WIN against {opponent}")
                
                # Display win probability
                prob_col1, prob_col2 = st.columns(2)
                with prob_col1:
                    st.metric("Win Probability", f"{win_probability:.1%}")
                    # Display confidence gauge
                    st.progress(float(win_probability))
                
                with prob_col2:
                    st.write("Key Factors (Feature Importance)")
                    # Show top 5 features
                    st.dataframe(feature_importance.head(5))
                
                # Create visualizations
                st.subheader("Visualizations")
                
                viz_col1, viz_col2 = st.columns(2)
                
                # Win probability gauge with Plotly
                with viz_col1:
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=win_probability * 100,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Win Probability (%)"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': "#1f77b4"},
                            'steps': [
                                {'range': [0, 33], 'color': "#ff7f0e"},
                                {'range': [33, 66], 'color': "#ffbb78"},
                                {'range': [66, 100], 'color': "#2ca02c"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 50
                            }
                        }
                    ))
                    st.plotly_chart(fig, use_container_width=True)
                
                # Feature importance bar chart
                with viz_col2:
                    top_features = feature_importance.head(10)
                    fig = px.bar(
                        top_features, 
                        x='Importance', 
                        y='Feature',
                        orientation='h',
                        title='Top 10 Most Important Factors',
                        color='Importance',
                        color_continuous_scale='Viridis'
                    )
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                
                # Historical form visualization if data is available
                if data is not None and 'team' in data.columns:
                    st.subheader("Team Form Analysis")
                    form_col1, form_col2 = st.columns(2)
                    
                    with form_col1:
                        team_data = data[data['team'] == team].sort_values('date')
                        if len(team_data) > 5:
                            team_data['result_code'] = team_data['result'].map({'W': 3, 'D': 1, 'L': 0})
                            team_data['cum_points'] = team_data['result_code'].cumsum()
                            
                            fig = px.line(
                                team_data.tail(10), 
                                x='date', 
                                y='cum_points',
                                title=f"{team} Points Accumulation (Last 10 Games)",
                                markers=True
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with form_col2:
                        # Head to head history if available
                        h2h_data = data[
                            ((data['team'] == team) & (data['opponent'] == opponent)) | 
                            ((data['team'] == opponent) & (data['opponent'] == team))
                        ].sort_values('date')
                        
                        if len(h2h_data) > 0:
                            st.write(f"Head-to-Head History: {team} vs {opponent}")
                            
                            h2h_results = pd.DataFrame({
                                'Date': h2h_data['date'],
                                'Home': h2h_data.apply(lambda x: x['team'] if x['venue'] == 'Home' else x['opponent'], axis=1),
                                'Away': h2h_data.apply(lambda x: x['opponent'] if x['venue'] == 'Home' else x['team'], axis=1),
                                'Score': h2h_data.apply(lambda x: f"{x['gf']}-{x['ga']}" if x['venue'] == 'Home' else f"{x['ga']}-{x['gf']}", axis=1),
                                'Result': h2h_data['result']
                            })
                            
                            st.dataframe(h2h_results)
                
                # Disclaimer
                st.caption("Note: This prediction is based on the uploaded data and should be used for educational purposes only.")
                
                # Prediction explanation
                st.info(f"""
                **Prediction Explanation**:
                The model analyzed {team}'s form, the venue advantage ({venue}), and historical performance against {opponent}. 
                Key factors in this prediction include recent goal-scoring record ({gf} goals per game), 
                defensive record ({ga} goals conceded per game), and shooting efficiency ({sot} shots on target from {sh} attempts).
                """)
    
    with tab2:
        st.header("View Current Dataset")
        
        # Add filters for the dataset
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            if 'team' in data.columns:
                team_filter = st.multiselect("Filter by Team", options=sorted(data['team'].unique()), default=[])
        
        with filter_col2:
            if 'date' in data.columns:
                min_date = data['date'].min().date()
                max_date = data['date'].max().date()
                date_range = st.date_input("Date Range", 
                                  value=(min_date, max_date),
                                  min_value=min_date,
                                  max_value=max_date)
        
        # Apply filters
        filtered_df = data.copy()
        if 'team' in data.columns and team_filter:
            filtered_df = filtered_df[filtered_df['team'].isin(team_filter)]
        
        if 'date' in data.columns and len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[(filtered_df['date'].dt.date >= start_date) & 
                                    (filtered_df['date'].dt.date <= end_date)]
        
        # Display filtered dataframe
        st.dataframe(filtered_df)
        
        # Download button for filtered data
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Filtered Data",
            csv,
            "filtered_data.csv",
            "text/csv",
            key='download-csv'
        )
    
    with tab3:
        st.header("Data Insights")
        
        if st.button("Generate Data Insights"):
            st.subheader("Match Results Distribution")
            if 'result' in data.columns:
                result_counts = data['result'].value_counts()
                
                # Create a pie chart
                fig = px.pie(
                    values=result_counts.values,
                    names=result_counts.index,
                    title="Result Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.write(f"Total Matches: {len(data)}")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("Result Distribution")
                    st.dataframe(result_counts)
                
                with col2:
                    st.write("Result Percentages")
                    st.dataframe(pd.DataFrame({
                        'Result': result_counts.index,
                        'Percentage': (result_counts.values / len(data) * 100).round(1)
                    }))
            
            # Team performance analysis
            st.subheader("Team Performance")
            if 'team' in data.columns and 'result' in data.columns:
                team_performance = data.groupby('team')['result'].value_counts().unstack().fillna(0)
                
                # Calculate win percentage
                if 'W' in team_performance.columns:
                    team_performance['Total'] = team_performance.sum(axis=1)
                    team_performance['Win%'] = (team_performance['W'] / team_performance['Total'] * 100).round(1)
                    team_performance = team_performance.sort_values('Win%', ascending=False)
                    
                    # Bar chart of win percentages
                    fig = px.bar(
                        x=team_performance.index,
                        y=team_performance['Win%'],
                        title="Win Percentage by Team",
                        labels={'x': 'Team', 'y': 'Win %'},
                        color=team_performance['Win%'],
                        color_continuous_scale='Viridis'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.dataframe(team_performance)
                
                # Home vs Away performance
                if 'venue' in data.columns:
                    st.subheader("Home vs Away Analysis")
                    venue_result = pd.crosstab(data['venue'], data['result'], normalize='index') * 100
                    venue_result = venue_result.round(1)
                    
                    # Create bar chart
                    if 'W' in venue_result.columns:
                        fig = px.bar(
                            x=['Home', 'Away'],
                            y=[venue_result.loc['Home', 'W'], venue_result.loc['Away', 'W']],
                            title="Win Percentage by Venue",
                            labels={'x': 'Venue', 'y': 'Win %'},
                            color=['Home', 'Away'],
                            color_discrete_sequence=['green', 'blue']
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    st.write("Win Percentage by Venue")
                    st.dataframe(venue_result)
                    
                    # Calculate overall home advantage
                    if 'W' in venue_result.columns and 'Home' in venue_result.index and 'Away' in venue_result.index:
                        home_advantage = venue_result.loc['Home', 'W'] - venue_result.loc['Away', 'W']
                        st.metric("Home Advantage (Win % difference)", f"{home_advantage:.1f}%")

# Footer
st.markdown("---")
st.markdown("Football Prediction System - Developed based on machine learning models for EPL match prediction")
st.caption("This application is for educational purposes only. Do not use for betting.")