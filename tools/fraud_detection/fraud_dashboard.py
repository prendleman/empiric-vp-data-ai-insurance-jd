"""
Executive Dashboard Generator for Fraud Detection Metrics
"""

import pandas as pd
import json
from datetime import datetime, timedelta
import numpy as np

class FraudDashboard:
    """Generates executive dashboards for fraud detection metrics."""
    
    def __init__(self, fraud_results_df=None, model_metrics=None):
        """
        Initialize dashboard generator.
        
        Args:
            fraud_results_df: DataFrame with fraud detection results
            model_metrics: Dictionary with model performance metrics
        """
        self.fraud_results = fraud_results_df
        self.model_metrics = model_metrics or {}
        self.dashboard_data = {}
    
    def generate_dashboard(self, output_path='fraud_dashboard.json'):
        """Generate dashboard data."""
        self._calculate_metrics()
        
        dashboard = {
            'metadata': {
                'title': 'Insurance Fraud Detection Dashboard',
                'generated_date': datetime.now().isoformat(),
                'version': '1.0'
            },
            'summary_metrics': self.dashboard_data.get('summary', {}),
            'model_performance': self.dashboard_data.get('model_performance', {}),
            'business_impact': self._calculate_business_impact(),
            'visualizations': self._create_visualizations()
        }
        
        with open(output_path, 'w') as f:
            json.dump(dashboard, f, indent=2, default=str)
        
        print(f"Dashboard saved to {output_path}")
        return dashboard
    
    def _calculate_metrics(self):
        """Calculate fraud detection metrics."""
        if self.fraud_results is None:
            # Generate sample metrics
            self.dashboard_data = {
                'summary': {
                    'total_claims_scored': 10000,
                    'fraudulent_claims_detected': 1500,
                    'fraud_rate': 0.15,
                    'average_fraud_score': 45.2
                },
                'model_performance': {
                    'precision': 0.82,
                    'recall': 0.75,
                    'f1_score': 0.78,
                    'roc_auc': 0.89
                }
            }
            return
        
        # Calculate from actual results
        total_claims = len(self.fraud_results)
        high_risk = len(self.fraud_results[self.fraud_results['risk_level'] == 'High'])
        medium_risk = len(self.fraud_results[self.fraud_results['risk_level'] == 'Medium'])
        
        self.dashboard_data = {
            'summary': {
                'total_claims_scored': total_claims,
                'high_risk_claims': high_risk,
                'medium_risk_claims': medium_risk,
                'low_risk_claims': total_claims - high_risk - medium_risk,
                'average_fraud_score': self.fraud_results['fraud_score'].mean(),
                'fraud_rate_estimate': (high_risk + medium_risk * 0.5) / total_claims
            },
            'model_performance': self.model_metrics
        }
    
    def _calculate_business_impact(self):
        """Calculate business impact and ROI."""
        summary = self.dashboard_data.get('summary', {})
        
        # Assumptions
        avg_claim_amount = 50000  # Average fraudulent claim amount
        fraud_prevention_rate = 0.75  # Percentage of fraud prevented
        total_claims = summary.get('total_claims_scored', 10000)
        fraud_rate = summary.get('fraud_rate_estimate', 0.15)
        
        # Calculate impact
        estimated_fraudulent_claims = total_claims * fraud_rate
        prevented_fraud = estimated_fraudulent_claims * fraud_prevention_rate
        cost_savings = prevented_fraud * avg_claim_amount
        
        # System costs (annual)
        system_cost = 500000  # $500K annual investment
        
        # ROI
        roi = ((cost_savings - system_cost) / system_cost) * 100 if system_cost > 0 else 0
        
        return {
            'estimated_fraudulent_claims': estimated_fraudulent_claims,
            'prevented_fraud_claims': prevented_fraud,
            'cost_savings_annual': cost_savings,
            'system_investment_annual': system_cost,
            'net_benefit_annual': cost_savings - system_cost,
            'roi_percentage': roi,
            'payback_period_months': (system_cost / (cost_savings / 12)) if cost_savings > 0 else 0
        }
    
    def _create_visualizations(self):
        """Create visualization definitions."""
        visualizations = []
        
        # Summary KPIs
        summary = self.dashboard_data.get('summary', {})
        visualizations.extend([
            {
                'type': 'kpi_card',
                'title': 'Total Claims Scored',
                'value': summary.get('total_claims_scored', 0),
                'format': 'number'
            },
            {
                'type': 'kpi_card',
                'title': 'High Risk Claims',
                'value': summary.get('high_risk_claims', 0),
                'format': 'number'
            },
            {
                'type': 'kpi_card',
                'title': 'Average Fraud Score',
                'value': summary.get('average_fraud_score', 0),
                'format': 'decimal'
            }
        ])
        
        # Model performance
        if 'model_performance' in self.dashboard_data:
            perf = self.dashboard_data['model_performance']
            visualizations.append({
                'type': 'gauge_chart',
                'title': 'Model Precision',
                'value': perf.get('precision', 0),
                'format': 'percentage'
            })
        
        # Business impact
        impact = self._calculate_business_impact()
        visualizations.extend([
            {
                'type': 'kpi_card',
                'title': 'Annual Cost Savings',
                'value': impact['cost_savings_annual'],
                'format': 'currency'
            },
            {
                'type': 'kpi_card',
                'title': 'ROI',
                'value': impact['roi_percentage'],
                'format': 'percentage'
            }
        ])
        
        return visualizations
    
    def generate_executive_summary(self):
        """Generate executive summary report."""
        summary = self.dashboard_data.get('summary', {})
        impact = self._calculate_business_impact()
        perf = self.dashboard_data.get('model_performance', {})
        
        return {
            'executive_summary': {
                'key_metrics': {
                    'claims_processed': summary.get('total_claims_scored', 0),
                    'fraud_detected': summary.get('high_risk_claims', 0),
                    'model_precision': f"{perf.get('precision', 0):.1%}",
                    'model_recall': f"{perf.get('recall', 0):.1%}"
                },
                'business_impact': {
                    'annual_cost_savings': f"${impact['cost_savings_annual']:,.0f}",
                    'roi': f"{impact['roi_percentage']:.1f}%",
                    'payback_period': f"{impact['payback_period_months']:.1f} months"
                },
                'recommendations': [
                    'Continue monitoring high-risk claims for pattern analysis',
                    'Refine model based on false positive feedback',
                    'Expand fraud detection to additional claim types',
                    'Integrate real-time scoring into claims processing workflow'
                ]
            }
        }

