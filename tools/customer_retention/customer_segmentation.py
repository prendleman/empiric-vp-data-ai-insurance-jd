"""
Customer Segmentation for Retention

Segments customers by churn risk and value for targeted retention strategies.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class CustomerSegmentation:
    """Segments customers for retention strategies."""
    
    def __init__(self, customer_data_df):
        """
        Initialize segmentation.
        
        Args:
            customer_data_df: DataFrame with customer data and churn predictions
        """
        self.customer_data = customer_data_df.copy()
        self.segments = None
        self.scaler = StandardScaler()
    
    def segment_by_risk_and_value(self, n_segments=4):
        """
        Segment customers by churn risk and customer value.
        
        Args:
            n_segments: Number of segments to create
            
        Returns:
            DataFrame with segment assignments
        """
        # Features for segmentation
        features = []
        
        if 'churn_risk_score' in self.customer_data.columns:
            features.append('churn_risk_score')
        if 'annual_premium' in self.customer_data.columns:
            features.append('annual_premium')
        if 'clv' in self.customer_data.columns:
            features.append('clv')
        elif 'expected_lifetime_years' in self.customer_data.columns:
            features.append('expected_lifetime_years')
        
        if len(features) == 0:
            raise ValueError("No suitable features found for segmentation")
        
        # Prepare data
        X = self.customer_data[features].fillna(0)
        X_scaled = self.scaler.fit_transform(X)
        
        # Cluster
        kmeans = KMeans(n_clusters=n_segments, random_state=42, n_init=10)
        self.customer_data['segment_id'] = kmeans.fit_predict(X_scaled)
        
        # Name segments
        self._name_segments()
        
        # Segment statistics
        self.segments = self.customer_data.groupby('segment_name').agg({
            'churn_risk_score': ['mean', 'count'],
            'annual_premium': 'mean' if 'annual_premium' in self.customer_data.columns else 'count',
            'churn_probability': 'mean' if 'churn_probability' in self.customer_data.columns else 'count'
        })
        
        return self.customer_data
    
    def _name_segments(self):
        """Name segments based on risk and value characteristics."""
        segment_stats = self.customer_data.groupby('segment_id').agg({
            'churn_risk_score': 'mean',
            'annual_premium': 'mean' if 'annual_premium' in self.customer_data.columns else 'count'
        })
        
        # Determine segment names
        risk_median = segment_stats['churn_risk_score'].median()
        value_median = segment_stats['annual_premium'].median()
        
        segment_names = {}
        for seg_id in segment_stats.index:
            risk = segment_stats.loc[seg_id, 'churn_risk_score']
            value = segment_stats.loc[seg_id, 'annual_premium']
            
            risk_label = 'High Risk' if risk >= risk_median else 'Low Risk'
            value_label = 'High Value' if value >= value_median else 'Low Value'
            
            segment_names[seg_id] = f"{risk_label} - {value_label}"
        
        self.customer_data['segment_name'] = self.customer_data['segment_id'].map(segment_names)
    
    def get_segment_strategies(self):
        """Get recommended strategies for each segment."""
        if self.segments is None:
            self.segment_by_risk_and_value()
        
        strategies = {}
        
        for segment_name in self.customer_data['segment_name'].unique():
            segment_data = self.customer_data[
                self.customer_data['segment_name'] == segment_name
            ]
            
            avg_risk = segment_data['churn_risk_score'].mean()
            avg_value = segment_data['annual_premium'].mean() if 'annual_premium' in segment_data.columns else 0
            
            if 'High Risk' in segment_name and 'High Value' in segment_name:
                strategies[segment_name] = {
                    'priority': 'Critical',
                    'strategy': 'Aggressive retention campaigns',
                    'recommended_actions': [
                        'Premium discounts',
                        'Personalized outreach',
                        'Product enhancements',
                        'Loyalty bonuses'
                    ],
                    'budget_allocation': 'High'
                }
            elif 'High Risk' in segment_name:
                strategies[segment_name] = {
                    'priority': 'High',
                    'strategy': 'Targeted retention campaigns',
                    'recommended_actions': [
                        'Personalized outreach',
                        'Payment plan options',
                        'Product education'
                    ],
                    'budget_allocation': 'Medium'
                }
            elif 'High Value' in segment_name:
                strategies[segment_name] = {
                    'priority': 'Medium',
                    'strategy': 'Proactive engagement',
                    'recommended_actions': [
                        'Regular check-ins',
                        'Value-added services',
                        'Upsell opportunities'
                    ],
                    'budget_allocation': 'Low'
                }
            else:
                strategies[segment_name] = {
                    'priority': 'Low',
                    'strategy': 'Standard retention',
                    'recommended_actions': [
                        'Standard communications',
                        'Automated renewals'
                    ],
                    'budget_allocation': 'Minimal'
                }
        
        return strategies

