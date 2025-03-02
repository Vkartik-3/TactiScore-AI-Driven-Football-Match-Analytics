from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.config import Base
from datetime import datetime

class Team(Base):
    """
    Represents a football team in the database
    """
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    matches = relationship("Match", back_populates="team")

class Match(Base):
    """
    Represents a football match in the database
    """
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    team_id = Column(Integer, ForeignKey('teams.id'))
    opponent = Column(String)
    venue = Column(String)
    
    # Match statistics
    goals_for = Column(Float)
    goals_against = Column(Float)
    shots = Column(Float)
    shots_on_target = Column(Float)
    result = Column(String)
    
    # Relationships
    team = relationship("Team", back_populates="matches")

class Prediction(Base):
    """
    Stores match predictions
    """
    __tablename__ = 'predictions'

    id = Column(Integer, primary_key=True, index=True)
    match_date = Column(DateTime, default=datetime.utcnow)
    team = Column(String)
    opponent = Column(String)
    win_probability = Column(Float)
    predicted_result = Column(String)
    model_version = Column(String)