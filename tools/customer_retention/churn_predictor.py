"""
Insurance Customer Churn Prediction Model

Predicts policyholder churn risk and calculates customer lifetime value.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler
import pickle
import warnings
warnings.filterwarnings('ignore')

class ChurnPredictor:
    """Predicts customer churn for insurance policyholders."""
    
    def __init__(self, data_path=None, policyholder_df=None, model_path=None):
        """
        Initialize churn predictor.
        
        Args:
            data_path: Path to CSV file with policyholder data
            policyholder_df: DataFrame with policyholder data
            model_path: Path to pre-trained model
        """
        if data_path:
            self.df = pd.read_csv(data_path)
        elif policyholder_df is not None:
            self.df = policyholder_df.copy()
        else:
            self.df = None
        
        if model_path:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
                self.model = model_data['model']
                self.scaler = model_data.get('scaler', StandardScaler())
                self.feature_names = model_data.get('feature_names', [])
        else:
            self.model = None
            self.scaler = StandardScaler()
            self.feature_names = []
    
    def prepare_features(self, df=None):
        """Prepare features for churn prediction."""
        if df is None:
            df = self.df.copy()
        
        features = df.copy()
        
        # Feature engineering
        if 'annual_premium' in features.columns and 'years_in_force' in features.columns:
            features['total_premium_paid'] = features['annual_premium'] * features['years_in_force']
        
        if 'issue_date' in features.columns:
            features['policy_age_days'] = (
                pd.to_datetime('now') - pd.to_datetime(features['issue_date'])
            ).dt.days
        
        # Premium change (if available)
        if 'current_premium' in features.columns and 'original_premium' in features.columns:
            features['premium_change_pct'] = (
                (features['current_premium'] - features['original_premium']) / 
                (features['original_premium'] + 1)
            )
        
        # Payment behavior
        if 'payment_frequency' in features.columns:
            payment_freq_map = {'Monthly': 12, 'Quarterly': 4, 'Annual': 1}
            features['payments_per_year'] = features['payment_frequency'].map(payment_freq_map)
        
        # Select numeric features
        numeric_cols = features.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove target variable if present
        if 'is_churned' in numeric_cols:
            numeric_cols.remove('is_churned')
        if 'churn' in numeric_cols:
            numeric_cols.remove('churn')
        
        return features[numeric_cols], numeric_cols
    
    def train_model(self, model_type='gradient_boosting'):
        """
        Train churn prediction model.
        
        Args:
            model_type: 'gradient_boosting' or 'random_forest'
        """
        if self.df is None:
            raise ValueError("No data available for training")
        
        # Prepare features
        X, feature_names = self.prepare_features()
        self.feature_names = feature_names
        
        # Target variable
        if 'is_churned' in self.df.columns:
            y = self.df['is_churned']
        elif 'churn' in self.df.columns:
            y = self.df['churn']
        else:
            raise ValueError("No churn target variable found. Need 'is_churned' or 'churn' column")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        if model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        else:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        print("\n=== Churn Prediction Model Performance ===")
        print(classification_report(y_test, y_pred))
        print(f"\nROC AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")
        
        return {
            'train_accuracy': self.model.score(X_train_scaled, y_train),
            'test_accuracy': self.model.score(X_test_scaled, y_test),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
    
    def predict_churn(self, policyholder_data=None):
        """
        Predict churn risk for policyholders.
        
        Args:
            policyholder_data: DataFrame with policyholder data (optional)
            
        Returns:
            DataFrame with churn predictions and scores
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        if policyholder_data is None:
            policyholder_data = self.df.copy()
        else:
            policyholder_data = policyholder_data.copy()
        
        # Prepare features
        X, _ = self.prepare_features(policyholder_data)
        
        # Ensure all feature columns exist
        for col in self.feature_names:
            if col not in X.columns:
                X[col] = 0
        
        X = X[self.feature_names]
        
        # Scale
        X_scaled = self.scaler.transform(X)
        
        # Predict
        churn_probability = self.model.predict_proba(X_scaled)[:, 1]
        churn_prediction = self.model.predict(X_scaled)
        
        # Create results
        results = policyholder_data.copy()
        results['churn_probability'] = churn_probability
        results['churn_prediction'] = churn_prediction
        results['churn_risk_score'] = churn_probability * 100
        
        # Risk level
        results['risk_level'] = results['churn_risk_score'].apply(
            lambda x: 'High' if x >= 70 else ('Medium' if x >= 40 else 'Low')
        )
        
        return results
    
    def calculate_clv(self, policyholder_data=None, discount_rate=0.05):
        """
        Calculate Customer Lifetime Value.
        
        Args:
            policyholder_data: DataFrame with policyholder data
            discount_rate: Discount rate for NPV calculation
            
        Returns:
            DataFrame with CLV calculations
        """
        if policyholder_data is None:
            policyholder_data = self.df.copy()
        else:
            policyholder_data = policyholder_data.copy()
        
        # Predict churn
        predictions = self.predict_churn(policyholder_data)
        
        # Calculate expected lifetime
        # Assume average policyholder lifetime is 10 years if low risk, 5 if medium, 2 if high
        lifetime_map = {'Low': 10, 'Medium': 5, 'High': 2}
        predictions['expected_lifetime_years'] = predictions['risk_level'].map(lifetime_map)
        
        # Calculate CLV (simplified)
        if 'annual_premium' in predictions.columns:
            predictions['clv'] = (
                predictions['annual_premium'] * 
                predictions['expected_lifetime_years'] *
                (1 - predictions['churn_probability'])
            )
            
            # Discounted CLV
            years = np.arange(1, predictions['expected_lifetime_years'].max() + 1)
            predictions['clv_discounted'] = predictions.apply(
                lambda row: sum(
                    row['annual_premium'] * (1 - row['churn_probability']) / ((1 + discount_rate) ** year)
                    for year in range(1, int(row['expected_lifetime_years']) + 1)
                ),
                axis=1
            )
        
        return predictions
    
    def save_model(self, model_path='churn_prediction_model.pkl'):
        """Save trained model."""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Model saved to {model_path}")

