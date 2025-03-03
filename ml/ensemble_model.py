# ml/ensemble_model.py
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import pandas as pd
import numpy as np
import joblib
from typing import List, Dict, Tuple, Optional, Union

class EnsemblePredictor:
    """
    Ensemble model that combines RandomForest and XGBoost predictions.
    """
    
    def __init__(self, 
                 rf_n_estimators=200, 
                 rf_min_samples_split=10,
                 xgb_n_estimators=100,
                 xgb_learning_rate=0.1,
                 xgb_max_depth=5,
                 weights=(0.5, 0.5),
                 model_version="1.0"):
        """
        Initialize the ensemble model with RandomForest and XGBoost.
        
        Args:
            rf_n_estimators: Number of trees in RandomForest
            rf_min_samples_split: Min samples required to split a node in RF
            xgb_n_estimators: Number of boosting rounds for XGBoost
            xgb_learning_rate: Learning rate for XGBoost
            xgb_max_depth: Maximum tree depth for XGBoost
            weights: Tuple of weights for (RandomForest, XGBoost)
            model_version: Version string for this model
        """
        # RandomForest model
        self.rf_model = RandomForestClassifier(
            n_estimators=rf_n_estimators,
            min_samples_split=rf_min_samples_split,
            random_state=42
        )
        
        # XGBoost model
        self.xgb_model = xgb.XGBClassifier(
            n_estimators=xgb_n_estimators,
            learning_rate=xgb_learning_rate,
            max_depth=xgb_max_depth,
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss'
        )
        
        # Weights for ensemble averaging
        self.weights = weights
        
        # Store hyperparameters
        self.hyperparams = {
            'rf_n_estimators': rf_n_estimators,
            'rf_min_samples_split': rf_min_samples_split,
            'xgb_n_estimators': xgb_n_estimators,
            'xgb_learning_rate': xgb_learning_rate,
            'xgb_max_depth': xgb_max_depth,
            'weights': weights
        }
        
        # Features and model version
        self.predictors = []
        self.model_version = model_version
        
        # Training metrics
        self.metrics = {}
        
    def train(self, X, y):
        """
        Train both models on the same data.
        
        Args:
            X: Training features
            y: Target variable
        """
        if len(X) == 0 or len(y) == 0:
            print("Warning: Empty training data")
            return self
            
        # Store feature names
        self.predictors = X.columns.tolist()
        
        # Train RandomForest
        print("Training RandomForest model...")
        self.rf_model.fit(X, y)
        
        # Train XGBoost
        print("Training XGBoost model...")
        self.xgb_model.fit(X, y)
        
        # Calculate feature importance
        self._calculate_feature_importance()
        
        return self
    
    def predict(self, X):
        """
        Make predictions using weighted ensemble.
        
        Args:
            X: Features to predict on
        
        Returns:
            Array of predictions (0 or 1)
        """
        # Get probability predictions
        rf_proba = self.rf_model.predict_proba(X)[:, 1]
        xgb_proba = self.xgb_model.predict_proba(X)[:, 1]
        
        # Weighted average
        ensemble_proba = self.weights[0] * rf_proba + self.weights[1] * xgb_proba
        
        # Convert to class predictions
        return (ensemble_proba > 0.5).astype(int)
    
    def predict_proba(self, X):
        """
        Return probability estimates for samples.
        
        Args:
            X: Features to predict on
            
        Returns:
            Array of probability estimates
        """
        if not hasattr(self.rf_model, 'classes_') or not hasattr(self.xgb_model, 'classes_'):
            # Models haven't been trained, return default
            return np.array([[0.5, 0.5] for _ in range(len(X))])
        
        # Get probability predictions from each model
        rf_proba = self.rf_model.predict_proba(X)
        xgb_proba = self.xgb_model.predict_proba(X)
        
        # Weighted average
        ensemble_proba = np.zeros_like(rf_proba)
        for i in range(rf_proba.shape[1]):
            ensemble_proba[:, i] = self.weights[0] * rf_proba[:, i] + self.weights[1] * xgb_proba[:, i]
            
        return ensemble_proba
        
    def _calculate_feature_importance(self):
        """Calculate and store feature importance from both models."""
        if not self.predictors:
            return
            
        # Get RF feature importance
        rf_importance = self.rf_model.feature_importances_
        
        # Get XGBoost feature importance
        xgb_importance = self.xgb_model.feature_importances_
        
        # Combine and create weighted importance DataFrame
        weighted_imp = pd.DataFrame({
            'Feature': self.predictors,
            'Importance': self.weights[0] * rf_importance + self.weights[1] * xgb_importance,
            'RF_Importance': rf_importance,
            'XGB_Importance': xgb_importance
        }).sort_values('Importance', ascending=False)
        
        self.feature_importance = weighted_imp
    
    def get_feature_importance(self):
        """
        Return feature importance in a DataFrame format.
        
        Returns:
            DataFrame with feature importance
        """
        if hasattr(self, 'feature_importance'):
            return self.feature_importance
        
        # Return default if not calculated
        return pd.DataFrame({
            'Feature': self.predictors if self.predictors else ['None'],
            'Importance': [0.2] * (len(self.predictors) if self.predictors else 1)
        })
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance on test data.
        
        Args:
            X_test: Test features
            y_test: Test targets
            
        Returns:
            Dictionary of evaluation metrics
        """
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        # Make predictions
        y_pred = self.predict(X_test)
        y_proba = self.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1': f1_score(y_test, y_pred, zero_division=0),
            'auc': roc_auc_score(y_test, y_proba)
        }
        
        # Get metrics for individual models
        rf_pred = self.rf_model.predict(X_test)
        rf_proba = self.rf_model.predict_proba(X_test)[:, 1]
        
        xgb_pred = self.xgb_model.predict(X_test)
        xgb_proba = self.xgb_model.predict_proba(X_test)[:, 1]
        
        metrics['rf_accuracy'] = accuracy_score(y_test, rf_pred)
        metrics['rf_auc'] = roc_auc_score(y_test, rf_proba)
        
        metrics['xgb_accuracy'] = accuracy_score(y_test, xgb_pred)
        metrics['xgb_auc'] = roc_auc_score(y_test, xgb_proba)
        
        # Store metrics
        self.metrics = metrics
        
        return metrics
    
    def save_model(self, filepath):
        """
        Save trained ensemble model to file.
        
        Args:
            filepath: Path to save the model
        """
        joblib.dump(self, filepath)
    
    @classmethod
    def load_model(cls, filepath):
        """
        Load trained ensemble model from file.
        
        Args:
            filepath: Path to load the model from
            
        Returns:
            Loaded model
        """
        try:
            return joblib.load(filepath)
        except Exception as e:
            print(f"Error loading model: {e}")
            return cls()