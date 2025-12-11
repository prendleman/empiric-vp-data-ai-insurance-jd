"""
Train fraud detection models on insurance claims data.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
import pickle
import warnings
warnings.filterwarnings('ignore')

def generate_sample_claims_data(num_claims=5000, fraud_rate=0.15):
    """
    Generate sample insurance claims data with fraud labels.
    
    Args:
        num_claims: Number of claims to generate
        fraud_rate: Percentage of fraudulent claims
        
    Returns:
        DataFrame with claims data and fraud labels
    """
    np.random.seed(42)
    
    claims = []
    
    for i in range(num_claims):
        is_fraud = np.random.random() < fraud_rate
        
        # Base claim amount
        if is_fraud:
            # Fraudulent claims tend to be larger
            claim_amount = np.random.lognormal(8, 1.5)
        else:
            claim_amount = np.random.lognormal(7, 1.0)
        
        # Policy premium
        policy_premium = np.random.uniform(500, 5000)
        
        # Days to claim (fraudulent claims often filed quickly)
        if is_fraud:
            days_to_claim = np.random.exponential(60)
        else:
            days_to_claim = np.random.exponential(365)
        
        # Claim type
        claim_types = ['Death', 'Disability', 'Critical Illness', 'Accidental Death']
        claim_type = np.random.choice(claim_types)
        
        # Policy age
        policy_age_years = np.random.uniform(0.1, 10)
        
        # Number of previous claims
        if is_fraud:
            prev_claims = np.random.poisson(0.5)
        else:
            prev_claims = np.random.poisson(0.2)
        
        # Beneficiary relationship
        beneficiary_relations = ['Spouse', 'Child', 'Parent', 'Other']
        beneficiary = np.random.choice(beneficiary_relations)
        
        # Suspicious patterns for fraud
        claim_to_premium_ratio = claim_amount / (policy_premium + 1)
        
        claims.append({
            'claim_id': f'CLM-{100000 + i}',
            'claim_amount': claim_amount,
            'policy_premium': policy_premium,
            'claim_to_premium_ratio': claim_to_premium_ratio,
            'days_to_claim': days_to_claim,
            'policy_age_years': policy_age_years,
            'claim_type': claim_type,
            'previous_claims': prev_claims,
            'beneficiary_relation': beneficiary,
            'is_fraud': 1 if is_fraud else 0
        })
    
    return pd.DataFrame(claims)

def train_fraud_model(data_path=None, claims_df=None, model_type='random_forest'):
    """
    Train fraud detection model.
    
    Args:
        data_path: Path to CSV file with claims data
        claims_df: DataFrame with claims data (if not using data_path)
        model_type: 'random_forest' or 'isolation_forest'
        
    Returns:
        Trained model and metrics
    """
    # Load data
    if data_path:
        df = pd.read_csv(data_path)
    elif claims_df is not None:
        df = claims_df.copy()
    else:
        # Generate sample data
        print("No data provided. Generating sample data...")
        df = generate_sample_claims_data()
    
    # Prepare features
    feature_cols = [
        'claim_amount', 'policy_premium', 'claim_to_premium_ratio',
        'days_to_claim', 'policy_age_years', 'previous_claims'
    ]
    
    # Add claim type encoding
    if 'claim_type' in df.columns:
        claim_type_dummies = pd.get_dummies(df['claim_type'], prefix='claim_type')
        df = pd.concat([df, claim_type_dummies], axis=1)
        feature_cols.extend(claim_type_dummies.columns)
    
    # Add beneficiary encoding
    if 'beneficiary_relation' in df.columns:
        beneficiary_dummies = pd.get_dummies(df['beneficiary_relation'], prefix='beneficiary')
        df = pd.concat([df, beneficiary_dummies], axis=1)
        feature_cols.extend(beneficiary_dummies.columns)
    
    # Select features
    X = df[[col for col in feature_cols if col in df.columns]]
    y = df['is_fraud'] if 'is_fraud' in df.columns else None
    
    # Split data
    if y is not None:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    else:
        # Unsupervised learning (isolation forest)
        X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
        y_train, y_test = None, None
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    if model_type == 'random_forest' and y_train is not None:
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        print("\n=== Model Performance ===")
        print(classification_report(y_test, y_pred))
        print(f"\nROC AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")
        
        metrics = {
            'model_type': 'RandomForestClassifier',
            'train_accuracy': model.score(X_train_scaled, y_train),
            'test_accuracy': model.score(X_test_scaled, y_test),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
        
    elif model_type == 'isolation_forest':
        model = IsolationForest(
            contamination=0.15,
            random_state=42,
            n_estimators=100
        )
        model.fit(X_train_scaled)
        
        # Evaluate (if labels available)
        y_pred = model.predict(X_test_scaled)
        y_pred_binary = (y_pred == -1).astype(int)  # -1 = anomaly (fraud)
        
        if y_test is not None:
            print("\n=== Model Performance ===")
            print(classification_report(y_test, y_pred_binary))
            
            metrics = {
                'model_type': 'IsolationForest',
                'classification_report': classification_report(y_test, y_pred_binary, output_dict=True)
            }
        else:
            metrics = {
                'model_type': 'IsolationForest',
                'anomalies_detected': (y_pred == -1).sum(),
                'anomaly_rate': (y_pred == -1).mean()
            }
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # Save model and scaler
    model_data = {
        'model': model,
        'scaler': scaler,
        'feature_names': list(X.columns),
        'metrics': metrics
    }
    
    return model_data

def save_model(model_data, model_path='fraud_detection_model.pkl'):
    """Save trained model to file."""
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    print(f"Model saved to {model_path}")

if __name__ == '__main__':
    # Generate sample data
    print("Generating sample claims data...")
    claims_data = generate_sample_claims_data(num_claims=5000)
    claims_data.to_csv('sample_claims_data.csv', index=False)
    print(f"Generated {len(claims_data)} claims")
    print(f"Fraud rate: {claims_data['is_fraud'].mean():.2%}")
    
    # Train model
    print("\nTraining fraud detection model...")
    model_data = train_fraud_model(claims_df=claims_data, model_type='random_forest')
    
    # Save model
    save_model(model_data, 'fraud_detection_model.pkl')
    print("\nModel training complete!")

