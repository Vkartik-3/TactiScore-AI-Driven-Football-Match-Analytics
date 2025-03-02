import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_matches(num_matches=100):
    # List of Premier League teams
    teams = [
        'Manchester City', 'Liverpool', 'Chelsea', 'Manchester United', 
        'Arsenal', 'Tottenham', 'Leicester City', 'West Ham', 
        'Newcastle United', 'Brighton', 'Wolves', 'Crystal Palace', 
        'Brentford', 'Southampton', 'Everton', 'Leeds United', 
        'Aston Villa', 'Watford', 'Norwich City', 'Burnley'
    ]

    # Generate sample data
    data = []
    start_date = datetime(2021, 8, 1)

    for _ in range(num_matches):
        team = np.random.choice(teams)
        opponent = np.random.choice([t for t in teams if t != team])
        
        # Random date within a season
        match_date = start_date + timedelta(days=np.random.randint(0, 300))
        
        # Randomize match statistics
        goals_for = np.random.randint(0, 5)
        goals_against = np.random.randint(0, 5)
        
        # Determine result
        if goals_for > goals_against:
            result = 'W'
        elif goals_for < goals_against:
            result = 'L'
        else:
            result = 'D'
        
        match_data = {
            'date': match_date.strftime('%Y-%m-%d'),
            'time': f'{np.random.randint(12,20):02d}:{np.random.randint(0,60):02d}',
            'team': team,
            'opponent': opponent,
            'venue': np.random.choice(['Home', 'Away']),
            'result': result,
            'gf': goals_for,
            'ga': goals_against,
            'sh': np.random.randint(5, 25),
            'sot': np.random.randint(1, 10),
            'dist': np.random.uniform(10, 20),
            'fk': np.random.randint(0, 5),
            'pk': np.random.randint(0, 2),
            'pkatt': np.random.randint(0, 2),
            'season': match_date.year
        }
        
        data.append(match_data)

    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv('data/matches.csv', index=False)
    print(f"Generated {num_matches} sample matches in data/matches.csv")

if __name__ == "__main__":
    generate_sample_matches()