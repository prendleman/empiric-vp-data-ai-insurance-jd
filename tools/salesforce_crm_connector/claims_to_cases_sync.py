"""
Claims to Cases Sync

Synchronizes insurance claims data to Salesforce Cases.
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from salesforce_connector import SalesforceConnector

class ClaimsToCasesSync:
    """Synchronizes claims data to Salesforce Cases."""
    
    def __init__(self, connector: SalesforceConnector):
        """
        Initialize claims to cases sync.
        
        Args:
            connector: SalesforceConnector instance
        """
        self.connector = connector
    
    def sync_claims_to_cases(self, claims_df: pd.DataFrame) -> Dict:
        """
        Sync claims data to Salesforce Cases.
        
        Args:
            claims_df: DataFrame with claims data
            
        Returns:
            Dictionary with sync results
        """
        results = {
            'cases_created': 0,
            'cases_updated': 0,
            'errors': []
        }
        
        for idx, claim in claims_df.iterrows():
            try:
                # Find associated account
                account = self.connector.get_account_by_policy_id(
                    claim.get('policy_id', '')
                )
                
                if not account:
                    results['errors'].append({
                        'claim_id': claim.get('claim_id', 'unknown'),
                        'error': 'Account not found'
                    })
                    continue
                
                case_data = self._prepare_case_data(claim, account['Id'])
                
                # Check if case exists
                soql = f"SELECT Id FROM Case WHERE Claim_ID__c = '{claim.get('claim_id', '')}' LIMIT 1"
                existing = self.connector.query(soql)
                
                if existing:
                    self.connector.update_record('Case', existing[0]['Id'], case_data)
                    results['cases_updated'] += 1
                else:
                    self.connector.create_case(case_data)
                    results['cases_created'] += 1
                
            except Exception as e:
                results['errors'].append({
                    'claim_id': claim.get('claim_id', 'unknown'),
                    'error': str(e)
                })
        
        return results
    
    def _prepare_case_data(self, claim: pd.Series, account_id: str) -> Dict:
        """Prepare case data from claim."""
        # Map claim status to case status
        status_mapping = {
            'Pending': 'New',
            'Approved': 'Closed',
            'Denied': 'Closed',
            'Under Review': 'In Progress'
        }
        
        case_status = status_mapping.get(
            claim.get('status', 'Pending'),
            'New'
        )
        
        case_data = {
            'AccountId': account_id,
            'Subject': f"Claim: {claim.get('claim_type', 'Insurance Claim')} - {claim.get('claim_id', '')}",
            'Status': case_status,
            'Priority': self._determine_priority(claim),
            'Claim_ID__c': claim.get('claim_id', ''),
            'Claim_Amount__c': claim.get('claim_amount', 0),
            'Claim_Type__c': claim.get('claim_type', ''),
            'Claim_Date__c': self._format_date(claim.get('claim_date')),
            'Description': self._create_case_description(claim),
            'Origin': 'Claims System',
            'Type': 'Claim'
        }
        
        return case_data
    
    def _determine_priority(self, claim: pd.Series) -> str:
        """Determine case priority based on claim characteristics."""
        amount = claim.get('claim_amount', 0)
        
        if amount > 100000:
            return 'High'
        elif amount > 50000:
            return 'Medium'
        else:
            return 'Low'
    
    def _create_case_description(self, claim: pd.Series) -> str:
        """Create case description from claim data."""
        description = f"Claim ID: {claim.get('claim_id', 'N/A')}\n"
        description += f"Claim Type: {claim.get('claim_type', 'N/A')}\n"
        description += f"Claim Amount: ${claim.get('claim_amount', 0):,.2f}\n"
        description += f"Status: {claim.get('status', 'N/A')}\n"
        
        if 'claim_date' in claim:
            description += f"Claim Date: {claim.get('claim_date')}\n"
        
        if 'description' in claim:
            description += f"\nDetails: {claim.get('description', '')}"
        
        return description
    
    def _format_date(self, date_value) -> Optional[str]:
        """Format date for Salesforce (YYYY-MM-DD)."""
        if pd.isna(date_value):
            return None
        
        try:
            if isinstance(date_value, str):
                date_obj = pd.to_datetime(date_value)
            else:
                date_obj = date_value
            
            return date_obj.strftime('%Y-%m-%d')
        except:
            return None

