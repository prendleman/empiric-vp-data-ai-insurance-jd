"""
Salesforce CRM Connector

Connects to Salesforce and provides methods for data synchronization
with Life & Annuity insurance systems.
"""

from simple_salesforce import Salesforce
import pandas as pd
from typing import Dict, List, Optional
import json
from datetime import datetime
import os

class SalesforceConnector:
    """Connects to Salesforce and provides CRM integration capabilities."""
    
    def __init__(self, username=None, password=None, security_token=None, 
                 domain='login', sandbox=False):
        """
        Initialize Salesforce connector.
        
        Args:
            username: Salesforce username
            password: Salesforce password
            security_token: Salesforce security token
            domain: 'login' for production, 'test' for sandbox
            sandbox: Boolean indicating if using sandbox
        """
        self.username = username or os.getenv('SALESFORCE_USERNAME')
        self.password = password or os.getenv('SALESFORCE_PASSWORD')
        self.security_token = security_token or os.getenv('SALESFORCE_SECURITY_TOKEN')
        self.domain = domain
        self.sandbox = sandbox
        
        self.sf = None
        if self.username and self.password and self.security_token:
            self._connect()
    
    def _connect(self):
        """Connect to Salesforce."""
        try:
            self.sf = Salesforce(
                username=self.username,
                password=self.password,
                security_token=self.security_token,
                domain=self.domain,
                sandbox=self.sandbox
            )
            print("Successfully connected to Salesforce")
        except Exception as e:
            print(f"Error connecting to Salesforce: {e}")
            raise
    
    def create_account(self, account_data: Dict) -> Dict:
        """
        Create an Account in Salesforce.
        
        Args:
            account_data: Dictionary with account fields
            
        Returns:
            Created account record
        """
        if not self.sf:
            raise Exception("Not connected to Salesforce")
        
        try:
            result = self.sf.Account.create(account_data)
            return result
        except Exception as e:
            print(f"Error creating account: {e}")
            raise
    
    def create_contact(self, contact_data: Dict) -> Dict:
        """
        Create a Contact in Salesforce.
        
        Args:
            contact_data: Dictionary with contact fields
            
        Returns:
            Created contact record
        """
        if not self.sf:
            raise Exception("Not connected to Salesforce")
        
        try:
            result = self.sf.Contact.create(contact_data)
            return result
        except Exception as e:
            print(f"Error creating contact: {e}")
            raise
    
    def create_opportunity(self, opportunity_data: Dict) -> Dict:
        """
        Create an Opportunity in Salesforce.
        
        Args:
            opportunity_data: Dictionary with opportunity fields
            
        Returns:
            Created opportunity record
        """
        if not self.sf:
            raise Exception("Not connected to Salesforce")
        
        try:
            result = self.sf.Opportunity.create(opportunity_data)
            return result
        except Exception as e:
            print(f"Error creating opportunity: {e}")
            raise
    
    def create_case(self, case_data: Dict) -> Dict:
        """
        Create a Case in Salesforce.
        
        Args:
            case_data: Dictionary with case fields
            
        Returns:
            Created case record
        """
        if not self.sf:
            raise Exception("Not connected to Salesforce")
        
        try:
            result = self.sf.Case.create(case_data)
            return result
        except Exception as e:
            print(f"Error creating case: {e}")
            raise
    
    def query(self, soql_query: str) -> List[Dict]:
        """
        Execute a SOQL query.
        
        Args:
            soql_query: SOQL query string
            
        Returns:
            List of records
        """
        if not self.sf:
            raise Exception("Not connected to Salesforce")
        
        try:
            result = self.sf.query(soql_query)
            return result['records']
        except Exception as e:
            print(f"Error executing query: {e}")
            raise
    
    def update_record(self, object_type: str, record_id: str, data: Dict) -> bool:
        """
        Update a record in Salesforce.
        
        Args:
            object_type: Salesforce object type (Account, Contact, etc.)
            record_id: Record ID
            data: Dictionary with fields to update
            
        Returns:
            True if successful
        """
        if not self.sf:
            raise Exception("Not connected to Salesforce")
        
        try:
            getattr(self.sf, object_type).update(record_id, data)
            return True
        except Exception as e:
            print(f"Error updating record: {e}")
            raise
    
    def bulk_create(self, object_type: str, records: List[Dict]) -> List[Dict]:
        """
        Bulk create records in Salesforce.
        
        Args:
            object_type: Salesforce object type
            records: List of record dictionaries
            
        Returns:
            List of created record results
        """
        if not self.sf:
            raise Exception("Not connected to Salesforce")
        
        try:
            results = []
            # Process in batches of 200 (Salesforce limit)
            for i in range(0, len(records), 200):
                batch = records[i:i+200]
                batch_results = getattr(self.sf.bulk, object_type).insert(batch)
                results.extend(batch_results)
            return results
        except Exception as e:
            print(f"Error in bulk create: {e}")
            raise
    
    def get_account_by_policy_id(self, policy_id: str) -> Optional[Dict]:
        """
        Find Account by policy ID (custom field).
        
        Args:
            policy_id: Policy ID to search for
            
        Returns:
            Account record or None
        """
        soql = f"SELECT Id, Name, Policy_ID__c FROM Account WHERE Policy_ID__c = '{policy_id}' LIMIT 1"
        results = self.query(soql)
        return results[0] if results else None
    
    def get_contact_by_email(self, email: str) -> Optional[Dict]:
        """
        Find Contact by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            Contact record or None
        """
        soql = f"SELECT Id, Name, Email FROM Contact WHERE Email = '{email}' LIMIT 1"
        results = self.query(soql)
        return results[0] if results else None

