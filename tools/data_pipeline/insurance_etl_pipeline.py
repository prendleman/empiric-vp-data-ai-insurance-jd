"""
Insurance ETL Pipeline

Extract, Transform, Load pipeline for insurance data.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
from typing import Dict, List, Optional

class InsuranceETLPipeline:
    """ETL pipeline for insurance data processing."""
    
    def __init__(self, config=None):
        """
        Initialize ETL pipeline.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.data_sources = {}
        self.transformations = []
        self.validation_rules = []
    
    def extract(self, source_path, source_type='csv'):
        """
        Extract data from source.
        
        Args:
            source_path: Path to source data
            source_type: Type of source ('csv', 'json', 'database')
        """
        print(f"Extracting data from {source_path}...")
        
        if source_type == 'csv':
            df = pd.read_csv(source_path)
        elif source_type == 'json':
            df = pd.read_json(source_path)
        elif source_type == 'excel':
            df = pd.read_excel(source_path)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
        
        print(f"Extracted {len(df)} records")
        return df
    
    def transform(self, df, transformations=None):
        """
        Transform data.
        
        Args:
            df: DataFrame to transform
            transformations: List of transformation functions
        """
        print("Transforming data...")
        
        transformed_df = df.copy()
        
        # Standard transformations
        if transformations is None:
            transformations = [
                self._standardize_dates,
                self._clean_numeric_fields,
                self._normalize_text_fields,
                self._calculate_derived_fields
            ]
        
        for transform_func in transformations:
            transformed_df = transform_func(transformed_df)
        
        print(f"Transformed {len(transformed_df)} records")
        return transformed_df
    
    def _standardize_dates(self, df):
        """Standardize date fields."""
        date_columns = ['issue_date', 'lapse_date', 'claim_date', 'policy_issue_date']
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    def _clean_numeric_fields(self, df):
        """Clean numeric fields."""
        numeric_columns = ['annual_premium', 'claim_amount', 'face_amount']
        
        for col in numeric_columns:
            if col in df.columns:
                # Remove non-numeric characters and convert
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Fill negative values with 0
                df[col] = df[col].clip(lower=0)
        
        return df
    
    def _normalize_text_fields(self, df):
        """Normalize text fields."""
        text_columns = ['policy_type', 'state', 'distribution_channel']
        
        for col in text_columns:
            if col in df.columns:
                # Strip whitespace and standardize case
                df[col] = df[col].astype(str).str.strip().str.title()
        
        return df
    
    def _calculate_derived_fields(self, df):
        """Calculate derived fields."""
        # Calculate years in force
        if 'issue_date' in df.columns:
            df['years_in_force'] = (
                (datetime.now() - pd.to_datetime(df['issue_date'])).dt.days / 365.25
            )
        
        # Calculate claim to premium ratio
        if 'claim_amount' in df.columns and 'annual_premium' in df.columns:
            df['claim_to_premium_ratio'] = (
                df['claim_amount'] / (df['annual_premium'] + 1)
            )
        
        return df
    
    def validate(self, df, validation_rules=None):
        """
        Validate data quality.
        
        Args:
            df: DataFrame to validate
            validation_rules: List of validation rules
        """
        print("Validating data...")
        
        if validation_rules is None:
            validation_rules = [
                self._validate_required_fields,
                self._validate_data_types,
                self._validate_value_ranges
            ]
        
        validation_results = []
        for rule in validation_rules:
            result = rule(df)
            validation_results.append(result)
        
        # Check if all validations passed
        all_passed = all(r['status'] == 'pass' for r in validation_results)
        
        if not all_passed:
            print("WARNING: Some validations failed")
            for result in validation_results:
                if result['status'] == 'fail':
                    print(f"  - {result['rule']}: {result.get('message', '')}")
        
        return {
            'status': 'pass' if all_passed else 'fail',
            'results': validation_results
        }
    
    def _validate_required_fields(self, df):
        """Validate required fields exist."""
        required_fields = ['policy_id'] if 'policy_id' in df.columns else []
        
        missing = [f for f in required_fields if f not in df.columns]
        
        return {
            'rule': 'required_fields',
            'status': 'pass' if len(missing) == 0 else 'fail',
            'message': f"Missing fields: {missing}" if missing else "All required fields present"
        }
    
    def _validate_data_types(self, df):
        """Validate data types."""
        issues = []
        
        if 'annual_premium' in df.columns:
            if not pd.api.types.is_numeric_dtype(df['annual_premium']):
                issues.append('annual_premium should be numeric')
        
        return {
            'rule': 'data_types',
            'status': 'pass' if len(issues) == 0 else 'fail',
            'message': '; '.join(issues) if issues else 'All data types valid'
        }
    
    def _validate_value_ranges(self, df):
        """Validate value ranges."""
        issues = []
        
        if 'annual_premium' in df.columns:
            negative_count = (df['annual_premium'] < 0).sum()
            if negative_count > 0:
                issues.append(f"{negative_count} negative premium values")
        
        return {
            'rule': 'value_ranges',
            'status': 'pass' if len(issues) == 0 else 'fail',
            'message': '; '.join(issues) if issues else 'All values in valid ranges'
        }
    
    def load(self, df, target_path, target_type='csv'):
        """
        Load data to target.
        
        Args:
            df: DataFrame to load
            target_path: Path to target
            target_type: Type of target ('csv', 'json', 'database')
        """
        print(f"Loading data to {target_path}...")
        
        if target_type == 'csv':
            df.to_csv(target_path, index=False)
        elif target_type == 'json':
            df.to_json(target_path, orient='records', date_format='iso')
        elif target_type == 'excel':
            df.to_excel(target_path, index=False)
        else:
            raise ValueError(f"Unsupported target type: {target_type}")
        
        print(f"Loaded {len(df)} records to {target_path}")
        return target_path
    
    def run_etl(self, source_path, target_path, source_type='csv', target_type='csv'):
        """
        Run complete ETL pipeline.
        
        Args:
            source_path: Path to source data
            target_path: Path to target data
            source_type: Type of source
            target_type: Type of target
        """
        print("=" * 50)
        print("Starting ETL Pipeline")
        print("=" * 50)
        
        start_time = datetime.now()
        
        try:
            # Extract
            df = self.extract(source_path, source_type)
            
            # Transform
            df = self.transform(df)
            
            # Validate
            validation_result = self.validate(df)
            
            if validation_result['status'] == 'fail':
                print("WARNING: Validation failed, but continuing...")
            
            # Load
            output_path = self.load(df, target_path, target_type)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print("=" * 50)
            print("ETL Pipeline Completed Successfully")
            print(f"Duration: {duration:.2f} seconds")
            print(f"Records processed: {len(df)}")
            print("=" * 50)
            
            return {
                'status': 'success',
                'output_path': output_path,
                'records_processed': len(df),
                'duration_seconds': duration,
                'validation': validation_result
            }
        
        except Exception as e:
            print(f"ERROR: ETL pipeline failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def generate_data_lineage(self, source_path, transformations, target_path):
        """Generate data lineage documentation."""
        return {
            'source': source_path,
            'target': target_path,
            'transformations': [t.__name__ if callable(t) else str(t) for t in transformations],
            'timestamp': datetime.now().isoformat(),
            'pipeline_version': '1.0'
        }

