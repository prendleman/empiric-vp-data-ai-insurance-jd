"""
Retention Campaign Optimizer

Optimizes retention campaigns based on churn predictions and customer segments.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from datetime import datetime, timedelta

class RetentionOptimizer:
    """Optimizes retention campaigns for at-risk policyholders."""
    
    def __init__(self, churn_predictions_df):
        """
        Initialize optimizer with churn predictions.
        
        Args:
            churn_predictions_df: DataFrame with churn predictions from ChurnPredictor
        """
        self.predictions = churn_predictions_df.copy()
        self.segments = None
    
    def segment_customers(self, n_segments=4, features=None):
        """
        Segment customers by churn risk and value.
        
        Args:
            n_segments: Number of segments to create
            features: List of feature columns to use for segmentation
        """
        if features is None:
            # Default features for segmentation
            features = ['churn_risk_score']
            if 'annual_premium' in self.predictions.columns:
                features.append('annual_premium')
            if 'clv' in self.predictions.columns:
                features.append('clv')
            elif 'expected_lifetime_years' in self.predictions.columns:
                features.append('expected_lifetime_years')
        
        # Select available features
        available_features = [f for f in features if f in self.predictions.columns]
        
        if len(available_features) == 0:
            # Fallback to risk score only
            available_features = ['churn_risk_score']
        
        # Prepare data for clustering
        X = self.predictions[available_features].fillna(0)
        
        # Normalize
        X_normalized = (X - X.mean()) / (X.std() + 1e-8)
        
        # Cluster
        kmeans = KMeans(n_clusters=n_segments, random_state=42, n_init=10)
        self.predictions['segment'] = kmeans.fit_predict(X_normalized)
        
        # Name segments based on risk and value
        self._name_segments()
        
        self.segments = self.predictions.groupby('segment').agg({
            'churn_risk_score': 'mean',
            'annual_premium': 'mean' if 'annual_premium' in self.predictions.columns else 'count',
            'churn_probability': 'mean'
        })
        
        return self.segments
    
    def _name_segments(self):
        """Name segments based on risk and value."""
        # Calculate segment characteristics
        segment_stats = self.predictions.groupby('segment').agg({
            'churn_risk_score': 'mean',
            'annual_premium': 'mean' if 'annual_premium' in self.predictions.columns else 'count'
        })
        
        # Name segments
        segment_names = {}
        for seg_id in segment_stats.index:
            risk = segment_stats.loc[seg_id, 'churn_risk_score']
            value = segment_stats.loc[seg_id, 'annual_premium']
            
            risk_level = 'High' if risk >= 50 else 'Low'
            value_level = 'High' if value >= segment_stats['annual_premium'].median() else 'Low'
            
            segment_names[seg_id] = f"{risk_level} Risk - {value_level} Value"
        
        self.predictions['segment_name'] = self.predictions['segment'].map(segment_names)
    
    def optimize_campaigns(self, budget=100000, campaign_types=None):
        """
        Optimize retention campaigns based on segments and budget.
        
        Args:
            budget: Total campaign budget
            campaign_types: Dictionary of campaign types and costs
            
        Returns:
            DataFrame with campaign recommendations
        """
        if campaign_types is None:
            campaign_types = {
                'Premium Discount': {'cost_per_customer': 500, 'effectiveness': 0.30},
                'Loyalty Bonus': {'cost_per_customer': 300, 'effectiveness': 0.25},
                'Personalized Outreach': {'cost_per_customer': 100, 'effectiveness': 0.20},
                'Product Enhancement': {'cost_per_customer': 200, 'effectiveness': 0.15}
            }
        
        recommendations = []
        
        # Prioritize high-risk, high-value customers
        high_priority = self.predictions[
            (self.predictions['churn_risk_score'] >= 60) &
            (self.predictions['annual_premium'] >= self.predictions['annual_premium'].quantile(0.5))
        ].copy()
        
        # Sort by risk score and value
        high_priority = high_priority.sort_values(
            by=['churn_risk_score', 'annual_premium'],
            ascending=[False, False]
        )
        
        remaining_budget = budget
        campaign_id = 1
        
        for idx, customer in high_priority.iterrows():
            if remaining_budget <= 0:
                break
            
            # Select best campaign for this customer
            best_campaign = None
            best_roi = 0
            
            for campaign_name, campaign_spec in campaign_types.items():
                cost = campaign_spec['cost_per_customer']
                effectiveness = campaign_spec['effectiveness']
                
                if cost > remaining_budget:
                    continue
                
                # Calculate expected value
                if 'annual_premium' in customer:
                    annual_premium = customer['annual_premium']
                    expected_retention_value = annual_premium * effectiveness
                    roi = (expected_retention_value - cost) / cost
                    
                    if roi > best_roi:
                        best_roi = roi
                        best_campaign = {
                            'campaign_name': campaign_name,
                            'cost': cost,
                            'effectiveness': effectiveness,
                            'expected_value': expected_retention_value,
                            'roi': roi
                        }
            
            if best_campaign:
                recommendations.append({
                    'campaign_id': campaign_id,
                    'customer_id': customer.get('policy_id', idx),
                    'churn_risk_score': customer['churn_risk_score'],
                    'annual_premium': customer.get('annual_premium', 0),
                    'campaign_type': best_campaign['campaign_name'],
                    'campaign_cost': best_campaign['cost'],
                    'expected_retention_value': best_campaign['expected_value'],
                    'expected_roi': best_campaign['roi'],
                    'priority': 'High'
                })
                
                remaining_budget -= best_campaign['cost']
                campaign_id += 1
        
        # Add medium priority customers if budget remains
        medium_priority = self.predictions[
            (self.predictions['churn_risk_score'] >= 40) &
            (self.predictions['churn_risk_score'] < 60) &
            (~self.predictions.index.isin([r['customer_id'] for r in recommendations]))
        ].copy()
        
        medium_priority = medium_priority.sort_values(
            by=['churn_risk_score', 'annual_premium'],
            ascending=[False, False]
        )
        
        for idx, customer in medium_priority.iterrows():
            if remaining_budget <= 0:
                break
            
            # Use lower-cost campaigns for medium priority
            for campaign_name, campaign_spec in campaign_types.items():
                if campaign_name == 'Personalized Outreach':
                    cost = campaign_spec['cost_per_customer']
                    effectiveness = campaign_spec['effectiveness']
                    
                    if cost <= remaining_budget:
                        annual_premium = customer.get('annual_premium', 0)
                        expected_retention_value = annual_premium * effectiveness
                        roi = (expected_retention_value - cost) / cost if cost > 0 else 0
                        
                        recommendations.append({
                            'campaign_id': campaign_id,
                            'customer_id': customer.get('policy_id', idx),
                            'churn_risk_score': customer['churn_risk_score'],
                            'annual_premium': annual_premium,
                            'campaign_type': campaign_name,
                            'campaign_cost': cost,
                            'expected_retention_value': expected_retention_value,
                            'expected_roi': roi,
                            'priority': 'Medium'
                        })
                        
                        remaining_budget -= cost
                        campaign_id += 1
                        break
        
        return pd.DataFrame(recommendations)
    
    def generate_ab_test_plan(self, test_duration_days=90):
        """
        Generate A/B testing plan for retention campaigns.
        
        Args:
            test_duration_days: Duration of A/B test in days
            
        Returns:
            Dictionary with A/B test plan
        """
        # Select test population (high-risk customers)
        test_population = self.predictions[
            self.predictions['churn_risk_score'] >= 50
        ].copy()
        
        # Split into control and treatment groups
        np.random.seed(42)
        test_population['group'] = np.random.choice(
            ['Control', 'Treatment'],
            size=len(test_population),
            p=[0.5, 0.5]
        )
        
        return {
            'test_duration_days': test_duration_days,
            'test_start_date': datetime.now(),
            'test_end_date': datetime.now() + timedelta(days=test_duration_days),
            'total_participants': len(test_population),
            'control_group_size': len(test_population[test_population['group'] == 'Control']),
            'treatment_group_size': len(test_population[test_population['group'] == 'Treatment']),
            'test_population': test_population[['policy_id', 'churn_risk_score', 'group']].to_dict('records'),
            'success_metrics': [
                'Churn rate reduction',
                'Retention rate improvement',
                'Customer lifetime value increase',
                'Campaign ROI'
            ]
        }

