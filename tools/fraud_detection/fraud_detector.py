"""
Insurance Claims Fraud Detection System

Uses machine learning to detect fraudulent insurance claims with
real-time scoring and model explainability.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class FraudDetector:
    """Detects fraudulent insurance claims using ML models."""
    
    def __init__(self, model_path=None, model=None):
        """
        Initialize fraud detector.
        
        Args:
            model_path: Path to saved model file
            model: Pre-trained model object
        """
        if model_path:
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
        elif model:
            self.model = model
        else:
            # Default model (will need training)
            self.model = None
        
        self.scaler = StandardScaler()
        self.feature_names = []
    
    def detect_fraud(self, claim_data):
        """
        Detect fraud in claim data.
        
        Args:
            claim_data: DataFrame or dict with claim features
            
        Returns:
            dict: Fraud detection results with score and prediction
        """
        if self.model is None:
            raise ValueError("Model not loaded. Please train or load a model first.")
        
        # Convert to DataFrame if needed
        if isinstance(claim_data, dict):
            claim_df = pd.DataFrame([claim_data])
        else:
            claim_df = claim_data.copy()
        
        # Prepare features
        features = self._prepare_features(claim_df)
        
        # Predict
        if hasattr(self.model, 'predict_proba'):
            # Classification model
            fraud_probability = self.model.predict_proba(features)[0][1]
            prediction = self.model.predict(features)[0]
        else:
            # Isolation Forest (anomaly detection)
            prediction = self.model.predict(features)[0]
            # Convert anomaly score to probability
            decision_score = self.model.decision_function(features)[0]
            fraud_probability = 1 / (1 + np.exp(-decision_score))  # Sigmoid transform
        
        # Fraud score (0-100)
        fraud_score = fraud_probability * 100
        
        # Risk level
        if fraud_score >= 75:
            risk_level = 'High'
        elif fraud_score >= 50:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        return {
            'fraud_score': float(fraud_score),
            'fraud_probability': float(fraud_probability),
            'prediction': 'Fraudulent' if prediction == 1 or fraud_score >= 50 else 'Legitimate',
            'risk_level': risk_level,
            'timestamp': datetime.now().isoformat()
        }
    
    def _prepare_features(self, claim_df):
        """Prepare features for model prediction."""
        # This should match the training feature engineering
        features = claim_df.copy()
        
        # Example feature engineering
        if 'claim_amount' in features.columns and 'policy_premium' in features.columns:
            features['claim_to_premium_ratio'] = (
                features['claim_amount'] / (features['policy_premium'] + 1)
            )
        
        if 'claim_date' in features.columns and 'policy_issue_date' in features.columns:
            features['days_to_claim'] = (
                pd.to_datetime(features['claim_date']) - 
                pd.to_datetime(features['policy_issue_date'])
            ).dt.days
        
        # Select numeric features
        numeric_cols = features.select_dtypes(include=[np.number]).columns
        features = features[numeric_cols]
        
        # Scale features
        if hasattr(self, 'scaler') and hasattr(self.scaler, 'mean_'):
            features = self.scaler.transform(features)
        else:
            # If scaler not fitted, just return features
            features = features.values
        
        return features
    
    def explain_prediction(self, claim_data, method='shap'):
        """
        Explain fraud prediction using SHAP or LIME.
        
        Args:
            claim_data: Claim data to explain
            method: 'shap' or 'lime'
            
        Returns:
            dict: Explanation of prediction
        """
        try:
            if method == 'shap':
                return self._explain_with_shap(claim_data)
            elif method == 'lime':
                return self._explain_with_lime(claim_data)
            else:
                return {'error': f'Unknown explanation method: {method}'}
        except ImportError:
            return {
                'error': f'{method.upper()} not installed. Install with: pip install {method}',
                'fallback': self._simple_explanation(claim_data)
            }
        except Exception as e:
            return {
                'error': str(e),
                'fallback': self._simple_explanation(claim_data)
            }
    
    def _explain_with_shap(self, claim_data):
        """Explain using SHAP values."""
        try:
            import shap
            
            # Prepare features
            if isinstance(claim_data, dict):
                claim_df = pd.DataFrame([claim_data])
            else:
                claim_df = claim_data.copy()
            
            features = self._prepare_features(claim_df)
            
            # Create explainer
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(features)
            
            # Get feature importance
            feature_importance = {}
            if isinstance(shap_values, list):
                shap_values = shap_values[1]  # For binary classification
            
            for i, value in enumerate(shap_values[0]):
                feature_name = f'feature_{i}'
                feature_importance[feature_name] = float(value)
            
            return {
                'method': 'SHAP',
                'feature_importance': feature_importance,
                'top_contributors': dict(sorted(
                    feature_importance.items(), 
                    key=lambda x: abs(x[1]), 
                    reverse=True
                )[:5])
            }
        except Exception as e:
            return {'error': f'SHAP explanation failed: {str(e)}'}
    
    def _explain_with_lime(self, claim_data):
        """Explain using LIME."""
        try:
            from lime import lime_tabular
            
            # This is a simplified version - full implementation would need training data
            return {
                'method': 'LIME',
                'note': 'LIME explanation requires training data. Using simplified explanation.',
                'fallback': self._simple_explanation(claim_data)
            }
        except Exception as e:
            return {'error': f'LIME explanation failed: {str(e)}'}
    
    def _simple_explanation(self, claim_data):
        """Simple feature-based explanation."""
        explanation = {
            'method': 'Feature Analysis',
            'factors': []
        }
        
        if isinstance(claim_data, dict):
            claim = claim_data
        else:
            claim = claim_data.iloc[0].to_dict()
        
        # Analyze key factors
        if 'claim_amount' in claim and 'policy_premium' in claim:
            ratio = claim['claim_amount'] / (claim.get('policy_premium', 1) + 1)
            if ratio > 10:
                explanation['factors'].append({
                    'factor': 'Claim to Premium Ratio',
                    'value': ratio,
                    'impact': 'High - Unusually large claim relative to premium'
                })
        
        if 'days_to_claim' in claim:
            days = claim['days_to_claim']
            if days < 30:
                explanation['factors'].append({
                    'factor': 'Days to Claim',
                    'value': days,
                    'impact': 'High - Claim filed very soon after policy issue'
                })
        
        return explanation
    
    def batch_detect(self, claims_df):
        """
        Detect fraud in batch of claims.
        
        Args:
            claims_df: DataFrame with multiple claims
            
        Returns:
            DataFrame: Claims with fraud scores added
        """
        results = []
        
        for idx, claim in claims_df.iterrows():
            result = self.detect_fraud(claim.to_dict())
            result['claim_id'] = claim.get('claim_id', idx)
            results.append(result)
        
        return pd.DataFrame(results)

