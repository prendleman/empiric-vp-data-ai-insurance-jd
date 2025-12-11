"""
Policy to CRM Sync

Synchronizes Life & Annuity policy data to Salesforce CRM.
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from salesforce_connector import SalesforceConnector

class PolicyToCRMSync:
    """Synchronizes policy data to Salesforce CRM."""
    
    def __init__(self, connector: SalesforceConnector):
        """
        Initialize policy to CRM sync.
        
        Args:
            connector: SalesforceConnector instance
        """
        self.connector = connector
    
    def sync_policies_to_accounts(self, policy_df: pd.DataFrame, 
                                  create_contacts: bool = True) -> Dict:
        """
        Sync policy data to Salesforce Accounts and Contacts.
        
        Args:
            policy_df: DataFrame with policy data
            create_contacts: Whether to create Contact records
            
        Returns:
            Dictionary with sync results
        """
        results = {
            'accounts_created': 0,
            'accounts_updated': 0,
            'contacts_created': 0,
            'contacts_updated': 0,
            'errors': []
        }
        
        for idx, policy in policy_df.iterrows():
            try:
                # Check if account exists
                existing_account = self.connector.get_account_by_policy_id(
                    policy.get('policy_id', '')
                )
                
                # Prepare account data
                account_data = self._prepare_account_data(policy)
                
                if existing_account:
                    # Update existing account
                    self.connector.update_record('Account', existing_account['Id'], account_data)
                    results['accounts_updated'] += 1
                    account_id = existing_account['Id']
                else:
                    # Create new account
                    account_result = self.connector.create_account(account_data)
                    results['accounts_created'] += 1
                    account_id = account_result['id']
                
                # Create or update contact if requested
                if create_contacts:
                    contact_result = self._sync_contact(policy, account_id)
                    if contact_result['created']:
                        results['contacts_created'] += 1
                    elif contact_result['updated']:
                        results['contacts_updated'] += 1
                
            except Exception as e:
                results['errors'].append({
                    'policy_id': policy.get('policy_id', 'unknown'),
                    'error': str(e)
                })
        
        return results
    
    def _prepare_account_data(self, policy: pd.Series) -> Dict:
        """Prepare account data from policy."""
        account_data = {
            'Name': self._get_account_name(policy),
            'Policy_ID__c': policy.get('policy_id', ''),
            'Policy_Type__c': policy.get('policy_type', ''),
            'Annual_Premium__c': policy.get('annual_premium', 0),
            'Policy_Status__c': policy.get('status', ''),
            'Issue_Date__c': self._format_date(policy.get('issue_date')),
            'BillingState': policy.get('state', ''),
            'Type': 'Policyholder'
        }
        
        # Add custom fields based on policy type
        if 'face_amount' in policy and pd.notna(policy['face_amount']):
            account_data['Face_Amount__c'] = policy['face_amount']
        
        if 'years_in_force' in policy and pd.notna(policy['years_in_force']):
            account_data['Years_in_Force__c'] = policy['years_in_force']
        
        return account_data
    
    def _get_account_name(self, policy: pd.Series) -> str:
        """Get account name from policy data."""
        # Try to construct name from available fields
        if 'first_name' in policy and 'last_name' in policy:
            return f"{policy.get('first_name', '')} {policy.get('last_name', '')}".strip()
        elif 'policyholder_name' in policy:
            return policy['policyholder_name']
        else:
            return f"Policyholder - {policy.get('policy_id', 'Unknown')}"
    
    def _sync_contact(self, policy: pd.Series, account_id: str) -> Dict:
        """Sync contact for policyholder."""
        result = {'created': False, 'updated': False}
        
        # Check if contact exists by email
        email = policy.get('email') or policy.get('policyholder_email')
        if not email:
            return result
        
        existing_contact = self.connector.get_contact_by_email(email)
        
        contact_data = {
            'AccountId': account_id,
            'Email': email,
            'FirstName': policy.get('first_name', ''),
            'LastName': policy.get('last_name', ''),
            'Phone': policy.get('phone', ''),
            'MailingState': policy.get('state', ''),
            'Policy_ID__c': policy.get('policy_id', '')
        }
        
        if existing_contact:
            # Update existing contact
            self.connector.update_record('Contact', existing_contact['Id'], contact_data)
            result['updated'] = True
        else:
            # Create new contact
            self.connector.create_contact(contact_data)
            result['created'] = True
        
        return result
    
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
    
    def sync_opportunities(self, opportunity_df: pd.DataFrame) -> Dict:
        """
        Sync sales opportunities to Salesforce.
        
        Args:
            opportunity_df: DataFrame with opportunity data
            
        Returns:
            Dictionary with sync results
        """
        results = {
            'opportunities_created': 0,
            'opportunities_updated': 0,
            'errors': []
        }
        
        for idx, opp in opportunity_df.iterrows():
            try:
                # Find associated account
                account = self.connector.get_account_by_policy_id(
                    opp.get('policy_id', '')
                )
                
                if not account:
                    results['errors'].append({
                        'opportunity': opp.get('name', 'unknown'),
                        'error': 'Account not found'
                    })
                    continue
                
                opportunity_data = {
                    'AccountId': account['Id'],
                    'Name': opp.get('name', 'New Policy Application'),
                    'StageName': opp.get('stage', 'Prospecting'),
                    'Amount': opp.get('amount', 0),
                    'CloseDate': self._format_date(opp.get('close_date', datetime.now())),
                    'Type': opp.get('type', 'New Business'),
                    'Probability': opp.get('probability', 50),
                    'Description': opp.get('description', '')
                }
                
                # Check if opportunity exists
                soql = f"SELECT Id FROM Opportunity WHERE AccountId = '{account['Id']}' AND Name = '{opportunity_data['Name']}' LIMIT 1"
                existing = self.connector.query(soql)
                
                if existing:
                    self.connector.update_record('Opportunity', existing[0]['Id'], opportunity_data)
                    results['opportunities_updated'] += 1
                else:
                    self.connector.create_opportunity(opportunity_data)
                    results['opportunities_created'] += 1
                
            except Exception as e:
                results['errors'].append({
                    'opportunity': opp.get('name', 'unknown'),
                    'error': str(e)
                })
        
        return results

