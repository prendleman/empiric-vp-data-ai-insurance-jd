"""
Retention ROI Calculator

Calculates ROI and business impact of retention initiatives.
"""

import pandas as pd
import numpy as np
from datetime import datetime

class RetentionROICalculator:
    """Calculates ROI for retention initiatives."""
    
    def __init__(self, churn_predictions_df, campaign_recommendations_df=None):
        """
        Initialize ROI calculator.
        
        Args:
            churn_predictions_df: DataFrame with churn predictions
            campaign_recommendations_df: DataFrame with campaign recommendations
        """
        self.predictions = churn_predictions_df.copy()
        self.campaigns = campaign_recommendations_df.copy() if campaign_recommendations_df is not None else None
    
    def calculate_retention_roi(self, baseline_churn_rate=0.15, target_churn_reduction=0.25):
        """
        Calculate ROI of retention analytics initiative.
        
        Args:
            baseline_churn_rate: Current churn rate without intervention
            target_churn_reduction: Target reduction in churn rate (e.g., 0.25 = 25% reduction)
        """
        # Calculate current state
        total_customers = len(self.predictions)
        
        if 'annual_premium' in self.predictions.columns:
            total_annual_premium = self.predictions['annual_premium'].sum()
            avg_annual_premium = self.predictions['annual_premium'].mean()
        else:
            # Estimate
            total_annual_premium = total_customers * 2000  # $2K average
            avg_annual_premium = 2000
        
        # Current churn impact
        current_churned_customers = total_customers * baseline_churn_rate
        current_churned_premium = total_annual_premium * baseline_churn_rate
        
        # Improved state (with retention analytics)
        improved_churn_rate = baseline_churn_rate * (1 - target_churn_reduction)
        improved_churned_customers = total_customers * improved_churn_rate
        improved_churned_premium = total_annual_premium * improved_churn_rate
        
        # Benefits
        customers_retained = current_churned_customers - improved_churned_customers
        premium_retained = current_churned_premium - improved_churned_premium
        
        # Costs
        analytics_investment = 300000  # $300K annual investment
        campaign_costs = 0
        
        if self.campaigns is not None and 'campaign_cost' in self.campaigns.columns:
            campaign_costs = self.campaigns['campaign_cost'].sum()
        
        total_investment = analytics_investment + campaign_costs
        
        # ROI
        net_benefit = premium_retained - total_investment
        roi_percentage = (net_benefit / total_investment) * 100 if total_investment > 0 else 0
        
        # Payback period
        monthly_benefit = premium_retained / 12
        payback_months = total_investment / monthly_benefit if monthly_benefit > 0 else 0
        
        return {
            'baseline_metrics': {
                'total_customers': total_customers,
                'baseline_churn_rate': baseline_churn_rate,
                'current_churned_customers': current_churned_customers,
                'current_churned_premium_annual': current_churned_premium
            },
            'improved_metrics': {
                'improved_churn_rate': improved_churn_rate,
                'improved_churned_customers': improved_churned_customers,
                'improved_churned_premium_annual': improved_churned_premium
            },
            'benefits': {
                'customers_retained': customers_retained,
                'premium_retained_annual': premium_retained,
                'churn_rate_reduction': target_churn_reduction
            },
            'costs': {
                'analytics_investment_annual': analytics_investment,
                'campaign_costs': campaign_costs,
                'total_investment': total_investment
            },
            'roi': {
                'net_benefit_annual': net_benefit,
                'roi_percentage': roi_percentage,
                'payback_period_months': payback_months
            }
        }
    
    def calculate_campaign_roi(self):
        """Calculate ROI for specific retention campaigns."""
        if self.campaigns is None:
            return {'error': 'No campaign recommendations provided'}
        
        # Calculate campaign-level ROI
        campaign_summary = self.campaigns.groupby('campaign_type').agg({
            'campaign_cost': 'sum',
            'expected_retention_value': 'sum',
            'customer_id': 'count'
        }).reset_index()
        
        campaign_summary['total_cost'] = campaign_summary['campaign_cost']
        campaign_summary['total_value'] = campaign_summary['expected_retention_value']
        campaign_summary['net_benefit'] = campaign_summary['total_value'] - campaign_summary['total_cost']
        campaign_summary['roi'] = (
            (campaign_summary['net_benefit'] / campaign_summary['total_cost']) * 100
        ).fillna(0)
        
        # Overall campaign ROI
        total_campaign_cost = self.campaigns['campaign_cost'].sum()
        total_expected_value = self.campaigns['expected_retention_value'].sum()
        overall_roi = ((total_expected_value - total_campaign_cost) / total_campaign_cost) * 100 if total_campaign_cost > 0 else 0
        
        return {
            'campaign_summary': campaign_summary.to_dict('records'),
            'overall_campaign_metrics': {
                'total_campaigns': len(self.campaigns),
                'total_campaign_cost': total_campaign_cost,
                'total_expected_value': total_expected_value,
                'net_benefit': total_expected_value - total_campaign_cost,
                'overall_roi': overall_roi
            }
        }
    
    def generate_executive_summary(self):
        """Generate executive summary of retention ROI."""
        roi_results = self.calculate_retention_roi()
        campaign_roi = self.calculate_campaign_roi() if self.campaigns is not None else None
        
        summary = {
            'retention_initiative_roi': {
                'annual_premium_retained': f"${roi_results['benefits']['premium_retained_annual']:,.0f}",
                'customers_retained': f"{roi_results['benefits']['customers_retained']:,.0f}",
                'total_investment': f"${roi_results['costs']['total_investment']:,.0f}",
                'net_benefit_annual': f"${roi_results['roi']['net_benefit_annual']:,.0f}",
                'roi_percentage': f"{roi_results['roi']['roi_percentage']:.1f}%",
                'payback_period': f"{roi_results['roi']['payback_period_months']:.1f} months"
            }
        }
        
        if campaign_roi and 'overall_campaign_metrics' in campaign_roi:
            summary['campaign_roi'] = {
                'total_campaign_cost': f"${campaign_roi['overall_campaign_metrics']['total_campaign_cost']:,.0f}",
                'expected_retention_value': f"${campaign_roi['overall_campaign_metrics']['total_expected_value']:,.0f}",
                'campaign_roi': f"{campaign_roi['overall_campaign_metrics']['overall_roi']:.1f}%"
            }
        
        return summary

