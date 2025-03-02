import pandas as pd
from sqlalchemy.orm import Session
from database.config import SessionLocal, engine
from database.models import Team, Match, Prediction
from datetime import datetime

def populate_database():
    # Create a database session
    db = SessionLocal()

    try:
        # Load data from CSV
        matches_df = pd.read_csv('data/matches.csv')

        # Populate Teams
        # Get unique teams
        unique_teams = set(matches_df['team'].unique())
        
        # Add teams to database
        for team_name in unique_teams:
            existing_team = db.query(Team).filter(Team.name == team_name).first()
            if not existing_team:
                new_team = Team(name=team_name)
                db.add(new_team)
        
        # Commit teams to database
        db.commit()

        # Populate Matches
        for _, match in matches_df.iterrows():
            # Check if match already exists to avoid duplicates
            existing_match = db.query(Match).filter(
                Match.date == pd.to_datetime(match['date']),
                Match.team_id == db.query(Team).filter(Team.name == match['team']).first().id
            ).first()

            if not existing_match:
                # Find the team's ID
                team = db.query(Team).filter(Team.name == match['team']).first()
                
                new_match = Match(
                    date=pd.to_datetime(match['date']),
                    team_id=team.id,
                    opponent=match['opponent'],
                    venue=match['venue'],
                    goals_for=match['gf'],
                    goals_against=match['ga'],
                    shots=match['sh'],
                    shots_on_target=match['sot'],
                    result=match['result']
                )
                db.add(new_match)
        
        # Commit matches to database
        db.commit()

        print("Database populated successfully!")

    except Exception as e:
        print(f"Error populating database: {e}")
        db.rollback()

    finally:
        db.close()

# This allows the script to be run directly
if __name__ == "__main__":
    populate_database()