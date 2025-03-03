from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from database.config import Base
from datetime import datetime
import json

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
    
    # Add reference to model version
    model_version_id = Column(Integer, ForeignKey('model_versions.id'), nullable=True)
    model_version_ref = relationship("ModelVersion", back_populates="predictions")

class ModelVersion(Base):
    """
    Stores information about different model versions
    """
    __tablename__ = 'model_versions'
    
    id = Column(Integer, primary_key=True, index=True)
    version_name = Column(String, unique=True, index=True)
    model_type = Column(String)  # 'randomforest', 'ensemble', etc.
    creation_date = Column(DateTime, default=datetime.utcnow)
    description = Column(Text, nullable=True)
    hyperparameters = Column(Text, nullable=True)  # JSON string of hyperparameters
    feature_importance = Column(Text, nullable=True)  # JSON string of feature importance
    metrics = Column(Text, nullable=True)  # JSON string of evaluation metrics
    
    # Associated predictions
    predictions = relationship("Prediction", back_populates="model_version_ref")
    
    def set_hyperparameters(self, params_dict):
        """Store hyperparameters as JSON string"""
        self.hyperparameters = json.dumps(params_dict)
    
    def get_hyperparameters(self):
        """Retrieve hyperparameters as dictionary"""
        if self.hyperparameters:
            return json.loads(self.hyperparameters)
        return {}
    
    def set_feature_importance(self, importance_df):
        """Store feature importance as JSON string"""
        if importance_df is not None:
            self.feature_importance = importance_df.to_json()
    
    def set_metrics(self, metrics_dict):
        """Store metrics as JSON string"""
        self.metrics = json.dumps(metrics_dict)
    
    def get_metrics(self):
        """Retrieve metrics as dictionary"""
        if self.metrics:
            return json.loads(self.metrics)
        return {}