"""
Data Quality Monitor

Monitors data quality metrics for insurance data pipelines.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class DataQualityMonitor:
    """Monitors data quality for insurance data."""
    
    def __init__(self):
        """Initialize data quality monitor."""
        self.quality_metrics = []
        self.thresholds = {
            'completeness': 0.95,  # 95% completeness required
            'accuracy': 0.90,      # 90% accuracy required
            'consistency': 0.95,    # 95% consistency required
            'validity': 0.98       # 98% validity required
        }
    
    def check_data_quality(self, data_path=None, df=None):
        """
        Check data quality metrics.
        
        Args:
            data_path: Path to data file
            df: DataFrame to check
            
        Returns:
            Dictionary with quality metrics
        """
        # Load data
        if data_path:
            df = pd.read_csv(data_path)
        elif df is not None:
            df = df.copy()
        else:
            raise ValueError("Must provide data_path or df")
        
        quality_report = {
            'timestamp': datetime.now().isoformat(),
            'total_records': len(df),
            'metrics': {}
        }
        
        # Completeness
        completeness = self._calculate_completeness(df)
        quality_report['metrics']['completeness'] = completeness
        
        # Accuracy (check for outliers and anomalies)
        accuracy = self._calculate_accuracy(df)
        quality_report['metrics']['accuracy'] = accuracy
        
        # Consistency
        consistency = self._calculate_consistency(df)
        quality_report['metrics']['consistency'] = consistency
        
        # Validity
        validity = self._calculate_validity(df)
        quality_report['metrics']['validity'] = validity
        
        # Overall quality score
        overall_score = (
            completeness['score'] * 0.25 +
            accuracy['score'] * 0.25 +
            consistency['score'] * 0.25 +
            validity['score'] * 0.25
        )
        
        quality_report['overall_quality_score'] = overall_score
        quality_report['quality_status'] = (
            'excellent' if overall_score >= 0.95 else
            ('good' if overall_score >= 0.85 else
             ('fair' if overall_score >= 0.75 else 'poor'))
        )
        
        return quality_report
    
    def _calculate_completeness(self, df):
        """Calculate data completeness."""
        total_cells = len(df) * len(df.columns)
        null_cells = df.isnull().sum().sum()
        completeness_ratio = 1 - (null_cells / total_cells) if total_cells > 0 else 1
        
        # Check critical fields
        critical_fields = ['policy_id'] if 'policy_id' in df.columns else []
        critical_completeness = 1.0
        
        if critical_fields:
            critical_nulls = df[critical_fields].isnull().sum().sum()
            critical_total = len(df) * len(critical_fields)
            critical_completeness = 1 - (critical_nulls / critical_total) if critical_total > 0 else 1
        
        return {
            'score': completeness_ratio,
            'null_count': int(null_cells),
            'total_cells': total_cells,
            'critical_fields_completeness': critical_completeness,
            'status': 'pass' if completeness_ratio >= self.thresholds['completeness'] else 'fail'
        }
    
    def _calculate_accuracy(self, df):
        """Calculate data accuracy (check for outliers)."""
        accuracy_issues = []
        
        # Check for negative values in positive fields
        if 'annual_premium' in df.columns:
            negative_premiums = (df['annual_premium'] < 0).sum()
            if negative_premiums > 0:
                accuracy_issues.append(f"{negative_premiums} negative premium values")
        
        # Check for unrealistic values
        if 'annual_premium' in df.columns:
            # Premiums over $1M are suspicious
            unrealistic = (df['annual_premium'] > 1000000).sum()
            if unrealistic > 0:
                accuracy_issues.append(f"{unrealistic} premiums over $1M")
        
        # Calculate accuracy score
        total_records = len(df)
        issue_count = sum(int(issue.split()[0]) for issue in accuracy_issues if issue.split()[0].isdigit())
        accuracy_ratio = 1 - (issue_count / total_records) if total_records > 0 else 1
        
        return {
            'score': accuracy_ratio,
            'issues': accuracy_issues,
            'issue_count': issue_count,
            'status': 'pass' if accuracy_ratio >= self.thresholds['accuracy'] else 'fail'
        }
    
    def _calculate_consistency(self, df):
        """Calculate data consistency."""
        consistency_issues = []
        
        # Check for duplicate records
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            consistency_issues.append(f"{duplicates} duplicate records")
        
        # Check for inconsistent values
        if 'status' in df.columns and 'lapse_date' in df.columns:
            # Active policies shouldn't have lapse dates
            inconsistent = ((df['status'] == 'Active') & (df['lapse_date'].notna())).sum()
            if inconsistent > 0:
                consistency_issues.append(f"{inconsistent} active policies with lapse dates")
        
        # Calculate consistency score
        total_records = len(df)
        issue_count = sum(int(issue.split()[0]) for issue in consistency_issues if issue.split()[0].isdigit())
        consistency_ratio = 1 - (issue_count / total_records) if total_records > 0 else 1
        
        return {
            'score': consistency_ratio,
            'issues': consistency_issues,
            'issue_count': issue_count,
            'status': 'pass' if consistency_ratio >= self.thresholds['consistency'] else 'fail'
        }
    
    def _calculate_validity(self, df):
        """Calculate data validity."""
        validity_issues = []
        
        # Check required fields
        required_fields = ['policy_id'] if 'policy_id' in df.columns else []
        for field in required_fields:
            null_count = df[field].isnull().sum()
            if null_count > 0:
                validity_issues.append(f"{null_count} null values in {field}")
        
        # Check data types
        if 'annual_premium' in df.columns:
            non_numeric = pd.to_numeric(df['annual_premium'], errors='coerce').isnull().sum()
            if non_numeric > 0:
                validity_issues.append(f"{non_numeric} non-numeric premium values")
        
        # Calculate validity score
        total_records = len(df)
        issue_count = sum(int(issue.split()[0]) for issue in validity_issues if issue.split()[0].isdigit())
        validity_ratio = 1 - (issue_count / total_records) if total_records > 0 else 1
        
        return {
            'score': validity_ratio,
            'issues': validity_issues,
            'issue_count': issue_count,
            'status': 'pass' if validity_ratio >= self.thresholds['validity'] else 'fail'
        }
    
    def monitor_over_time(self, data_paths, time_period_days=30):
        """
        Monitor data quality over time.
        
        Args:
            data_paths: List of (timestamp, data_path) tuples
            time_period_days: Time period to analyze
        """
        quality_trends = []
        
        for timestamp, path in data_paths:
            try:
                df = pd.read_csv(path)
                quality_report = self.check_data_quality(df=df)
                quality_trends.append({
                    'timestamp': timestamp,
                    'quality_score': quality_report['overall_quality_score'],
                    'status': quality_report['quality_status']
                })
            except Exception as e:
                print(f"Error processing {path}: {e}")
        
        return {
            'trends': quality_trends,
            'average_quality': np.mean([t['quality_score'] for t in quality_trends]) if quality_trends else 0,
            'trend_direction': self._calculate_trend(quality_trends)
        }
    
    def _calculate_trend(self, trends):
        """Calculate quality trend direction."""
        if len(trends) < 2:
            return 'insufficient_data'
        
        recent_scores = [t['quality_score'] for t in trends[-5:]]
        earlier_scores = [t['quality_score'] for t in trends[:5]]
        
        if len(recent_scores) > 0 and len(earlier_scores) > 0:
            recent_avg = np.mean(recent_scores)
            earlier_avg = np.mean(earlier_scores)
            
            if recent_avg > earlier_avg * 1.05:
                return 'improving'
            elif recent_avg < earlier_avg * 0.95:
                return 'declining'
        
        return 'stable'

