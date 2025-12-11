"""
Generate realistic sample Life & Annuity policy data for analytics demonstrations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_data(num_policies=10000, start_date='2020-01-01'):
    """
    Generate realistic sample Life & Annuity policy data.
    
    Args:
        num_policies: Number of policies to generate
        start_date: Start date for policy issuance
        
    Returns:
        DataFrame with policy data
    """
    np.random.seed(42)
    random.seed(42)
    
    # Policy types
    policy_types = ['Term Life', 'Whole Life', 'Universal Life', 'Variable Annuity', 
                   'Fixed Annuity', 'Indexed Annuity']
    
    # Distribution channels
    channels = ['Agent', 'Broker', 'Direct', 'Online', 'Bank', 'Worksite']
    
    # States
    states = ['CA', 'TX', 'FL', 'NY', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
    
    # Generate policy data
    data = []
    base_date = pd.to_datetime(start_date)
    
    for i in range(num_policies):
        policy_type = np.random.choice(policy_types, p=[0.25, 0.15, 0.15, 0.15, 0.15, 0.15])
        channel = np.random.choice(channels, p=[0.30, 0.25, 0.15, 0.10, 0.10, 0.10])
        
        # Issue date (spread over 5 years)
        days_offset = np.random.randint(0, 1825)
        issue_date = base_date + timedelta(days=days_offset)
        
        # Policyholder age at issue
        age_at_issue = np.random.randint(25, 70)
        
        # Premium amount (varies by policy type and age)
        base_premium = {
            'Term Life': 500 + age_at_issue * 20,
            'Whole Life': 2000 + age_at_issue * 50,
            'Universal Life': 1500 + age_at_issue * 40,
            'Variable Annuity': 5000 + age_at_issue * 100,
            'Fixed Annuity': 3000 + age_at_issue * 60,
            'Indexed Annuity': 4000 + age_at_issue * 80
        }
        annual_premium = base_premium[policy_type] * (1 + np.random.normal(0, 0.2))
        annual_premium = max(100, annual_premium)  # Minimum premium
        
        # Face amount (for life insurance)
        if 'Life' in policy_type:
            face_amount = annual_premium * np.random.uniform(50, 200)
        else:
            face_amount = annual_premium * np.random.uniform(10, 50)
        
        # Lapse probability (higher for term, lower for annuities)
        lapse_base = {
            'Term Life': 0.15,
            'Whole Life': 0.05,
            'Universal Life': 0.10,
            'Variable Annuity': 0.03,
            'Fixed Annuity': 0.02,
            'Indexed Annuity': 0.02
        }
        lapse_prob = lapse_base[policy_type]
        
        # Adjust for age (younger = higher lapse)
        if age_at_issue < 35:
            lapse_prob *= 1.5
        elif age_at_issue > 60:
            lapse_prob *= 0.7
        
        # Current status
        years_in_force = (datetime.now() - issue_date).days / 365.25
        
        if years_in_force > 0 and np.random.random() < lapse_prob * min(years_in_force / 5, 1):
            status = 'Lapsed'
            lapse_date = issue_date + timedelta(days=np.random.randint(90, int(years_in_force * 365)))
        else:
            status = 'Active'
            lapse_date = None
        
        # State
        state = np.random.choice(states)
        
        # Gender
        gender = np.random.choice(['M', 'F'], p=[0.48, 0.52])
        
        # Payment frequency
        payment_freq = np.random.choice(['Monthly', 'Quarterly', 'Annual'], p=[0.60, 0.25, 0.15])
        
        data.append({
            'policy_id': f'POL-{1000000 + i}',
            'policy_type': policy_type,
            'issue_date': issue_date,
            'age_at_issue': age_at_issue,
            'current_age': age_at_issue + years_in_force,
            'annual_premium': round(annual_premium, 2),
            'face_amount': round(face_amount, 2) if 'Life' in policy_type else None,
            'distribution_channel': channel,
            'state': state,
            'gender': gender,
            'payment_frequency': payment_freq,
            'status': status,
            'lapse_date': lapse_date,
            'years_in_force': round(years_in_force, 2),
            'premium_paid_to_date': round(annual_premium * years_in_force * (0.85 if status == 'Active' else 0.5), 2)
        })
    
    df = pd.DataFrame(data)
    return df

def generate_cohort_data(policy_df):
    """
    Generate cohort analysis data from policy DataFrame.
    
    Args:
        policy_df: DataFrame with policy data
        
    Returns:
        DataFrame with cohort analysis metrics
    """
    policy_df['issue_year'] = pd.to_datetime(policy_df['issue_date']).dt.year
    policy_df['issue_quarter'] = pd.to_datetime(policy_df['issue_date']).dt.to_period('Q')
    
    cohort_data = []
    
    for cohort in policy_df['issue_quarter'].unique():
        cohort_policies = policy_df[policy_df['issue_quarter'] == cohort]
        
        for period in range(0, 21):  # 5 years of quarters
            period_date = pd.to_datetime(str(cohort)) + pd.DateOffset(months=period*3)
            
            if period_date > datetime.now():
                break
            
            # Policies still active at this period
            active_at_period = cohort_policies[
                (cohort_policies['status'] == 'Active') | 
                ((cohort_policies['lapse_date'].notna()) & 
                 (pd.to_datetime(cohort_policies['lapse_date']) > period_date))
            ]
            
            total_policies = len(cohort_policies)
            active_policies = len(active_at_period)
            retention_rate = active_policies / total_policies if total_policies > 0 else 0
            
            cohort_data.append({
                'cohort': str(cohort),
                'period': period,
                'period_date': period_date,
                'total_policies': total_policies,
                'active_policies': active_policies,
                'retention_rate': retention_rate,
                'cumulative_premium': active_at_period['premium_paid_to_date'].sum()
            })
    
    return pd.DataFrame(cohort_data)

if __name__ == '__main__':
    # Generate sample data
    print("Generating sample policy data...")
    policy_data = generate_sample_data(num_policies=10000)
    print(f"Generated {len(policy_data)} policies")
    print(f"\nPolicy Types Distribution:")
    print(policy_data['policy_type'].value_counts())
    print(f"\nStatus Distribution:")
    print(policy_data['status'].value_counts())
    
    # Save to CSV
    policy_data.to_csv('sample_policy_data.csv', index=False)
    print(f"\nSaved to sample_policy_data.csv")
    
    # Generate cohort data
    print("\nGenerating cohort analysis data...")
    cohort_data = generate_cohort_data(policy_data)
    cohort_data.to_csv('sample_cohort_data.csv', index=False)
    print(f"Saved to sample_cohort_data.csv")

