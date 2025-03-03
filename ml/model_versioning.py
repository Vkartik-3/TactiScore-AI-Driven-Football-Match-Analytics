# ml/model_versioning.py
from datetime import datetime
import os
import json
import pandas as pd
import joblib
from database.config import SessionLocal
from database.models import ModelVersion
from typing import Dict, Any, Optional, Union

class ModelVersionTracker:
    """
    Tracks and manages model versions, including metadata and performance metrics.
    """
    
    def __init__(self, model_dir: str = "../models"):
        """
        Initialize the model version tracker.
        
        Args:
            model_dir: Directory to store model files
        """
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
    
    def register_model(
        self, 
        model: Any, 
        model_type: str,
        version_name: Optional[str] = None,
        description: Optional[str] = None,
        hyperparameters: Optional[Dict] = None,
        metrics: Optional[Dict] = None,
    ) -> str:
        """
        Register a new model version in the database and save model file.
        
        Args:
            model: The trained model object
            model_type: Type of model (e.g., 'randomforest', 'ensemble')
            version_name: Optional version name (generated if not provided)
            description: Optional description of the model
            hyperparameters: Optional dictionary of model hyperparameters
            metrics: Optional dictionary of evaluation metrics
            
        Returns:
            The version name of the registered model
        """
        # Generate version name if not provided
        if not version_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            version_name = f"{model_type}_{timestamp}"
        
        # Extract feature importance from model if available
        feature_importance = None
        if hasattr(model, 'get_feature_importance'):
            feature_importance = model.get_feature_importance()
        elif hasattr(model, 'feature_importances_'):
            # For scikit-learn models
            if hasattr(model, 'feature_names_in_'):
                feature_importance = pd.DataFrame({
                    'Feature': model.feature_names_in_,
                    'Importance': model.feature_importances_
                }).sort_values('Importance', ascending=False)
        
        # Save model file
        model_path = os.path.join(self.model_dir, f"{version_name}.pkl")
        joblib.dump(model, model_path)
        
        # Create database entry
        db = SessionLocal()
        try:
            model_version = ModelVersion(
                version_name=version_name,
                model_type=model_type,
                description=description
            )
            
            # Store hyperparameters
            if hyperparameters:
                model_version.set_hyperparameters(hyperparameters)
                
            # Store feature importance
            if feature_importance is not None:
                model_version.set_feature_importance(feature_importance)
            
            # Store metrics
            if metrics:
                model_version.set_metrics(metrics)
            
            db.add(model_version)
            db.commit()
            db.refresh(model_version)
            
            print(f"Registered model version: {version_name}")
            return version_name
            
        except Exception as e:
            db.rollback()
            print(f"Error registering model version: {e}")
            return version_name
        finally:
            db.close()
    
    def get_model_versions(self, model_type: Optional[str] = None) -> list:
        """
        Get all registered model versions, optionally filtered by type.
        
        Args:
            model_type: Optional filter by model type
            
        Returns:
            List of model version information
        """
        db = SessionLocal()
        try:
            query = db.query(ModelVersion)
            if model_type:
                query = query.filter(ModelVersion.model_type == model_type)
            
            versions = query.order_by(ModelVersion.creation_date.desc()).all()
            
            # Convert to list of dictionaries
            result = []
            for version in versions:
                result.append({
                    'id': version.id,
                    'version_name': version.version_name,
                    'model_type': version.model_type,
                    'creation_date': version.creation_date.isoformat(),
                    'description': version.description,
                    'metrics': version.get_metrics(),
                    # Hyperparameters can be large, so exclude by default
                })
            
            return result
        
        finally:
            db.close()
    
    def get_latest_version(self, model_type: str) -> Optional[str]:
        """
        Get the latest version name for a given model type.
        
        Args:
            model_type: The model type to filter by
            
        Returns:
            The latest version name or None
        """
        db = SessionLocal()
        try:
            latest = db.query(ModelVersion).filter(
                ModelVersion.model_type == model_type
            ).order_by(ModelVersion.creation_date.desc()).first()
            
            return latest.version_name if latest else None
            
        finally:
            db.close()
    
    def load_model(self, version_name: Optional[str] = None, model_type: Optional[str] = None) -> Any:
        """
        Load a model by version name or latest version of a model type.
        
        Args:
            version_name: Specific version to load
            model_type: Model type to load the latest version of
            
        Returns:
            The loaded model object or None if not found
        """
        if not version_name and model_type:
            version_name = self.get_latest_version(model_type)
        
        if not version_name:
            print("No version name provided and no latest version found")
            return None
        
        model_path = os.path.join(self.model_dir, f"{version_name}.pkl")
        
        try:
            if os.path.exists(model_path):
                return joblib.load(model_path)
            else:
                print(f"Model file not found: {model_path}")
                return None
        except Exception as e:
            print(f"Error loading model: {e}")
            return None
    
    def get_version_details(self, version_name: str) -> Optional[Dict]:
        """
        Get detailed information about a specific model version.
        
        Args:
            version_name: The version name to get details for
            
        Returns:
            Dictionary of version details or None if not found
        """
        db = SessionLocal()
        try:
            version = db.query(ModelVersion).filter(
                ModelVersion.version_name == version_name
            ).first()
            
            if not version:
                return None
            
            # Prepare return dictionary with all details
            return {
                'id': version.id,
                'version_name': version.version_name,
                'model_type': version.model_type,
                'creation_date': version.creation_date.isoformat(),
                'description': version.description,
                'hyperparameters': version.get_hyperparameters(),
                'metrics': version.get_metrics(),
            }
            
        finally:
            db.close()