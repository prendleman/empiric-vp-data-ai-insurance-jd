"""
Life & Annuity Policy Data Analyzer

Analyzes policy data to provide insights on lapse rates, premium trends, 
mortality patterns, and policy retention.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

class PolicyAnalyzer:
    """Analyzes Life & Annuity policy data for business insights."""
    
    def __init__(self, policy_df):
        """
        Initialize analyzer with policy data.
        
        Args:
            policy_df: DataFrame with policy data
        """
        self.policy_df = policy_df.copy()
        self.results = {}
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare data for analysis."""
        # Ensure dates are datetime
        if 'issue_date' in self.policy_df.columns:
            self.policy_df['issue_date'] = pd.to_datetime(self.policy_df['issue_date'])
        
        if 'lapse_date' in self.policy_df.columns:
            self.policy_df['lapse_date'] = pd.to_datetime(self.policy_df['lapse_date'], errors='coerce')
        
        # Calculate additional metrics
        if 'issue_date' in self.policy_df.columns:
            self.policy_df['years_in_force'] = (
                (datetime.now() - self.policy_df['issue_date']).dt.days / 365.25
            )
        
        # Create lapse flag
        self.policy_df['is_lapsed'] = (self.policy_df['status'] == 'Lapsed').astype(int)
    
    def analyze(self):
        """
        Perform comprehensive policy analysis.
        
        Returns:
            dict: Analysis results
        """
        self.results = {
            'summary': self._calculate_summary_stats(),
            'lapse_analysis': self._analyze_lapse_rates(),
            'premium_trends': self._analyze_premium_trends(),
            'cohort_analysis': self._analyze_cohorts(),
            'product_performance': self._analyze_product_performance(),
            'lapse_prediction': self._build_lapse_prediction_model(),
            'roi_metrics': self._calculate_roi_metrics()
        }
        return self.results
    
    def _calculate_summary_stats(self):
        """Calculate summary statistics."""
        total_policies = len(self.policy_df)
        active_policies = len(self.policy_df[self.policy_df['status'] == 'Active'])
        lapsed_policies = len(self.policy_df[self.policy_df['status'] == 'Lapsed'])
        
        total_premium = self.policy_df['annual_premium'].sum()
        active_premium = self.policy_df[self.policy_df['status'] == 'Active']['annual_premium'].sum()
        
        return {
            'total_policies': total_policies,
            'active_policies': active_policies,
            'lapsed_policies': lapsed_policies,
            'overall_lapse_rate': lapsed_policies / total_policies if total_policies > 0 else 0,
            'total_annual_premium': total_premium,
            'active_annual_premium': active_premium,
            'lapsed_annual_premium': total_premium - active_premium,
            'average_premium': self.policy_df['annual_premium'].mean(),
            'average_years_in_force': self.policy_df['years_in_force'].mean()
        }
    
    def _analyze_lapse_rates(self):
        """Analyze lapse rates by various dimensions."""
        analysis = {}
        
        # By policy type
        if 'policy_type' in self.policy_df.columns:
            lapse_by_type = self.policy_df.groupby('policy_type').agg({
                'is_lapsed': ['sum', 'count', 'mean']
            }).round(4)
            lapse_by_type.columns = ['lapsed_count', 'total_count', 'lapse_rate']
            analysis['by_policy_type'] = lapse_by_type.to_dict('index')
        
        # By distribution channel
        if 'distribution_channel' in self.policy_df.columns:
            lapse_by_channel = self.policy_df.groupby('distribution_channel').agg({
                'is_lapsed': ['sum', 'count', 'mean']
            }).round(4)
            lapse_by_channel.columns = ['lapsed_count', 'total_count', 'lapse_rate']
            analysis['by_channel'] = lapse_by_channel.to_dict('index')
        
        # By years in force
        if 'years_in_force' in self.policy_df.columns:
            self.policy_df['years_bucket'] = pd.cut(
                self.policy_df['years_in_force'],
                bins=[0, 1, 2, 3, 5, 10, 100],
                labels=['0-1', '1-2', '2-3', '3-5', '5-10', '10+']
            )
            lapse_by_years = self.policy_df.groupby('years_bucket').agg({
                'is_lapsed': ['sum', 'count', 'mean']
            }).round(4)
            lapse_by_years.columns = ['lapsed_count', 'total_count', 'lapse_rate']
            analysis['by_years_in_force'] = lapse_by_years.to_dict('index')
        
        # By state
        if 'state' in self.policy_df.columns:
            lapse_by_state = self.policy_df.groupby('state').agg({
                'is_lapsed': ['sum', 'count', 'mean']
            }).round(4)
            lapse_by_state.columns = ['lapsed_count', 'total_count', 'lapse_rate']
            analysis['by_state'] = lapse_by_state.to_dict('index')
        
        return analysis
    
    def _analyze_premium_trends(self):
        """Analyze premium trends over time."""
        if 'issue_date' not in self.policy_df.columns:
            return {}
        
        self.policy_df['issue_year'] = pd.to_datetime(self.policy_df['issue_date']).dt.year
        self.policy_df['issue_quarter'] = pd.to_datetime(self.policy_df['issue_date']).dt.to_period('Q')
        
        # Premium by year
        premium_by_year = self.policy_df.groupby('issue_year').agg({
            'annual_premium': ['sum', 'mean', 'count']
        })
        premium_by_year.columns = ['total_premium', 'avg_premium', 'policy_count']
        
        # Premium by quarter
        premium_by_quarter = self.policy_df.groupby('issue_quarter').agg({
            'annual_premium': ['sum', 'mean', 'count']
        })
        premium_by_quarter.columns = ['total_premium', 'avg_premium', 'policy_count']
        
        return {
            'by_year': premium_by_year.to_dict('index'),
            'by_quarter': {str(k): v for k, v in premium_by_quarter.to_dict('index').items()},
            'trend_direction': self._calculate_trend_direction(premium_by_year['avg_premium'])
        }
    
    def _calculate_trend_direction(self, series):
        """Calculate if trend is increasing or decreasing."""
        if len(series) < 2:
            return 'insufficient_data'
        
        recent = series.tail(3).mean()
        earlier = series.head(3).mean()
        
        if recent > earlier * 1.05:
            return 'increasing'
        elif recent < earlier * 0.95:
            return 'decreasing'
        else:
            return 'stable'
    
    def _analyze_cohorts(self):
        """Perform cohort analysis."""
        if 'issue_date' not in self.policy_df.columns:
            return {}
        
        self.policy_df['issue_quarter'] = pd.to_datetime(self.policy_df['issue_date']).dt.to_period('Q')
        
        cohort_results = []
        
        for cohort in sorted(self.policy_df['issue_quarter'].unique()):
            cohort_policies = self.policy_df[self.policy_df['issue_quarter'] == cohort]
            
            # Calculate retention at different periods
            for period in [0, 1, 2, 4, 8, 12]:  # 0, 1Q, 2Q, 1Y, 2Y, 3Y
                period_date = pd.to_datetime(str(cohort)) + pd.DateOffset(months=period*3)
                
                if period_date > datetime.now():
                    break
                
                # Policies still active
                active = cohort_policies[
                    (cohort_policies['status'] == 'Active') |
                    ((cohort_policies['lapse_date'].notna()) &
                     (pd.to_datetime(cohort_policies['lapse_date']) > period_date))
                ]
                
                retention_rate = len(active) / len(cohort_policies) if len(cohort_policies) > 0 else 0
                
                cohort_results.append({
                    'cohort': str(cohort),
                    'period_quarters': period,
                    'retention_rate': retention_rate,
                    'total_policies': len(cohort_policies),
                    'active_policies': len(active)
                })
        
        return pd.DataFrame(cohort_results).to_dict('records')
    
    def _analyze_product_performance(self):
        """Analyze performance by product type."""
        if 'policy_type' not in self.policy_df.columns:
            return {}
        
        product_perf = self.policy_df.groupby('policy_type').agg({
            'annual_premium': ['sum', 'mean', 'count'],
            'is_lapsed': 'mean',
            'years_in_force': 'mean',
            'premium_paid_to_date': 'sum'
        }).round(2)
        
        product_perf.columns = [
            'total_premium', 'avg_premium', 'policy_count', 
            'lapse_rate', 'avg_years_in_force', 'total_premium_collected'
        ]
        
        return product_perf.to_dict('index')
    
    def _build_lapse_prediction_model(self):
        """Build ML model to predict policy lapse."""
        try:
            # Prepare features
            feature_cols = []
            
            if 'policy_type' in self.policy_df.columns:
                policy_type_dummies = pd.get_dummies(self.policy_df['policy_type'], prefix='type')
                feature_cols.extend(policy_type_dummies.columns)
                X = policy_type_dummies.copy()
            else:
                X = pd.DataFrame()
            
            if 'age_at_issue' in self.policy_df.columns:
                X['age_at_issue'] = self.policy_df['age_at_issue']
                feature_cols.append('age_at_issue')
            
            if 'annual_premium' in self.policy_df.columns:
                X['annual_premium'] = self.policy_df['annual_premium']
                feature_cols.append('annual_premium')
            
            if 'years_in_force' in self.policy_df.columns:
                X['years_in_force'] = self.policy_df['years_in_force']
                feature_cols.append('years_in_force')
            
            if 'distribution_channel' in self.policy_df.columns:
                channel_dummies = pd.get_dummies(self.policy_df['distribution_channel'], prefix='channel')
                X = pd.concat([X, channel_dummies], axis=1)
                feature_cols.extend(channel_dummies.columns)
            
            if len(X) == 0 or 'is_lapsed' not in self.policy_df.columns:
                return {'error': 'Insufficient data for model training'}
            
            y = self.policy_df['is_lapsed']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train model
            model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
            model.fit(X_train, y_train)
            
            # Evaluate
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            
            y_pred = model.predict(X_test)
            feature_importance = dict(zip(feature_cols, model.feature_importances_))
            
            return {
                'model_type': 'RandomForestClassifier',
                'train_accuracy': float(train_score),
                'test_accuracy': float(test_score),
                'feature_importance': {k: float(v) for k, v in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]},
                'sample_size': len(X)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_roi_metrics(self):
        """Calculate ROI metrics for analytics initiatives."""
        summary = self.results.get('summary', {}) if self.results else self._calculate_summary_stats()
        
        total_premium = summary.get('total_annual_premium', 0)
        lapsed_premium = summary.get('lapsed_annual_premium', 0)
        lapse_rate = summary.get('overall_lapse_rate', 0)
        
        # Estimated impact of analytics-driven retention improvement
        # Assuming 15% reduction in lapse rate
        improvement_rate = 0.15
        potential_premium_retained = lapsed_premium * improvement_rate
        
        # Cost of analytics initiative (estimated)
        analytics_cost = 500000  # $500K annual investment
        
        # ROI calculation
        roi = ((potential_premium_retained - analytics_cost) / analytics_cost) * 100 if analytics_cost > 0 else 0
        
        return {
            'current_lapse_rate': lapse_rate,
            'target_lapse_rate_reduction': improvement_rate,
            'potential_premium_retained_annual': potential_premium_retained,
            'analytics_investment_annual': analytics_cost,
            'net_benefit_annual': potential_premium_retained - analytics_cost,
            'roi_percentage': roi,
            'payback_period_months': (analytics_cost / (potential_premium_retained / 12)) if potential_premium_retained > 0 else 0
        }
    
    def get_executive_summary(self):
        """Generate executive summary of analysis."""
        if not self.results:
            self.analyze()
        
        summary = self.results['summary']
        roi = self.results['roi_metrics']
        
        return {
            'total_policies': summary['total_policies'],
            'active_policies': summary['active_policies'],
            'lapse_rate': f"{summary['overall_lapse_rate']:.2%}",
            'total_annual_premium': f"${summary['total_annual_premium']:,.0f}",
            'potential_roi': f"{roi['roi_percentage']:.1f}%",
            'potential_annual_benefit': f"${roi['net_benefit_annual']:,.0f}",
            'key_insights': [
                f"Current lapse rate: {summary['overall_lapse_rate']:.2%}",
                f"Potential premium retention: ${roi['potential_premium_retained_annual']:,.0f} annually",
                f"ROI of analytics initiative: {roi['roi_percentage']:.1f}%"
            ]
        }

