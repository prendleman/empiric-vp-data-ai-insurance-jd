"""
Data Governance Checker

Validates data quality and governance for compliance requirements.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json

class DataGovernanceChecker:
    """Checks data quality and governance for compliance."""
    
    def __init__(self):
        """Initialize data governance checker."""
        self.validation_rules = {
            'required_fields': ['policy_id', 'policy_type', 'issue_date'],
            'data_types': {
                'policy_id': 'string',
                'annual_premium': 'numeric',
                'issue_date': 'date'
            },
            'value_ranges': {
                'annual_premium': {'min': 0, 'max': 1000000},
                'age_at_issue': {'min': 18, 'max': 100}
            }
        }
    
    def validate_data_quality(self, data_path=None, df=None):
        """
        Validate data quality for compliance.
        
        Args:
            data_path: Path to data file
            df: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        # Load data
        if data_path:
            df = pd.read_csv(data_path)
        elif df is not None:
            df = df.copy()
        else:
            raise ValueError("Must provide data_path or df")
        
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'total_records': len(df),
            'checks': {}
        }
        
        # Check required fields
        missing_fields = []
        for field in self.validation_rules['required_fields']:
            if field not in df.columns:
                missing_fields.append(field)
        
        validation_results['checks']['required_fields'] = {
            'status': 'pass' if len(missing_fields) == 0 else 'fail',
            'missing_fields': missing_fields
        }
        
        # Check data types
        type_issues = []
        for field, expected_type in self.validation_rules['data_types'].items():
            if field in df.columns:
                if expected_type == 'numeric':
                    if not pd.api.types.is_numeric_dtype(df[field]):
                        type_issues.append(f"{field}: expected numeric, got {df[field].dtype}")
                elif expected_type == 'date':
                    try:
                        pd.to_datetime(df[field])
                    except:
                        type_issues.append(f"{field}: expected date, got {df[field].dtype}")
        
        validation_results['checks']['data_types'] = {
            'status': 'pass' if len(type_issues) == 0 else 'fail',
            'issues': type_issues
        }
        
        # Check value ranges
        range_issues = []
        for field, ranges in self.validation_rules['value_ranges'].items():
            if field in df.columns:
                if ranges.get('min') is not None:
                    below_min = (df[field] < ranges['min']).sum()
                    if below_min > 0:
                        range_issues.append(f"{field}: {below_min} values below minimum {ranges['min']}")
                if ranges.get('max') is not None:
                    above_max = (df[field] > ranges['max']).sum()
                    if above_max > 0:
                        range_issues.append(f"{field}: {above_max} values above maximum {ranges['max']}")
        
        validation_results['checks']['value_ranges'] = {
            'status': 'pass' if len(range_issues) == 0 else 'fail',
            'issues': range_issues
        }
        
        # Check for duplicates
        duplicate_count = df.duplicated().sum()
        validation_results['checks']['duplicates'] = {
            'status': 'pass' if duplicate_count == 0 else 'fail',
            'duplicate_count': int(duplicate_count)
        }
        
        # Check for nulls in critical fields
        null_issues = {}
        for field in self.validation_rules['required_fields']:
            if field in df.columns:
                null_count = df[field].isnull().sum()
                if null_count > 0:
                    null_issues[field] = int(null_count)
        
        validation_results['checks']['null_values'] = {
            'status': 'pass' if len(null_issues) == 0 else 'fail',
            'null_counts': null_issues
        }
        
        # Overall status
        all_passed = all(
            check['status'] == 'pass' 
            for check in validation_results['checks'].values()
        )
        validation_results['overall_status'] = 'pass' if all_passed else 'fail'
        
        return validation_results
    
    def generate_data_lineage(self, data_path, transformations=None):
        """
        Generate data lineage for audit purposes.
        
        Args:
            data_path: Path to data file
            transformations: List of transformations applied
            
        Returns:
            Dictionary with data lineage information
        """
        lineage = {
            'source_file': data_path,
            'timestamp': datetime.now().isoformat(),
            'transformations': transformations or [],
            'data_quality_checks': self.validate_data_quality(data_path)
        }
        
        return lineage
    
    def calculate_compliance_score(self, validation_results):
        """
        Calculate compliance score based on validation results.
        
        Args:
            validation_results: Results from validate_data_quality
            
        Returns:
            Compliance score (0-100)
        """
        total_checks = len(validation_results['checks'])
        passed_checks = sum(
            1 for check in validation_results['checks'].values()
            if check['status'] == 'pass'
        )
        
        score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        return {
            'compliance_score': score,
            'passed_checks': passed_checks,
            'total_checks': total_checks,
            'status': 'compliant' if score >= 90 else ('needs_attention' if score >= 70 else 'non_compliant')
        }

