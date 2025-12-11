"""
CRM Analytics Integration

Integrates Salesforce CRM data with analytics and reporting systems.
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from salesforce_connector import SalesforceConnector

class CRMAnalyticsIntegration:
    """Integrates Salesforce CRM data with analytics systems."""
    
    def __init__(self, connector: SalesforceConnector):
        """
        Initialize CRM analytics integration.
        
        Args:
            connector: SalesforceConnector instance
        """
        self.connector = connector
    
    def get_sales_pipeline_data(self, days_back: int = 90) -> pd.DataFrame:
        """
        Get sales pipeline data from Salesforce.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            DataFrame with opportunity data
        """
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        soql = f"""
        SELECT Id, Name, AccountId, Account.Name, StageName, Amount, 
               CloseDate, Type, Probability, CreatedDate, LastModifiedDate
        FROM Opportunity
        WHERE CreatedDate >= {start_date}T00:00:00Z
        ORDER BY CreatedDate DESC
        """
        
        opportunities = self.connector.query(soql)
        
        # Convert to DataFrame
        df = pd.DataFrame(opportunities)
        
        # Clean up nested fields
        if 'Account' in df.columns:
            df['Account_Name'] = df['Account'].apply(
                lambda x: x.get('Name', '') if isinstance(x, dict) else ''
            )
            df = df.drop('Account', axis=1, errors='ignore')
        
        return df
    
    def get_agent_performance_data(self) -> pd.DataFrame:
        """
        Get agent performance data from Salesforce.
        
        Returns:
            DataFrame with agent performance metrics
        """
        # Query opportunities grouped by owner (agent)
        soql = """
        SELECT OwnerId, Owner.Name, COUNT(Id) as Opportunity_Count,
               SUM(Amount) as Total_Amount, AVG(Amount) as Avg_Amount,
               SUM(CASE WHEN StageName = 'Closed Won' THEN Amount ELSE 0 END) as Won_Amount
        FROM Opportunity
        WHERE CreatedDate = THIS_YEAR
        GROUP BY OwnerId, Owner.Name
        """
        
        # Note: This is a simplified query - actual implementation would use
        # Salesforce Reports API or aggregate queries
        
        opportunities = self.connector.query(soql)
        df = pd.DataFrame(opportunities)
        
        return df
    
    def get_customer_360_view(self, account_id: str) -> Dict:
        """
        Get 360-degree view of a customer from Salesforce.
        
        Args:
            account_id: Salesforce Account ID
            
        Returns:
            Dictionary with customer data
        """
        # Get account details
        soql_account = f"SELECT Id, Name, Policy_ID__c, Annual_Premium__c, Policy_Status__c FROM Account WHERE Id = '{account_id}'"
        account = self.connector.query(soql_account)
        
        # Get related opportunities
        soql_opps = f"SELECT Id, Name, StageName, Amount, CloseDate FROM Opportunity WHERE AccountId = '{account_id}'"
        opportunities = self.connector.query(soql_opps)
        
        # Get related cases
        soql_cases = f"SELECT Id, Subject, Status, Claim_Amount__c, Claim_Type__c FROM Case WHERE AccountId = '{account_id}'"
        cases = self.connector.query(soql_cases)
        
        # Get related contacts
        soql_contacts = f"SELECT Id, Name, Email, Phone FROM Contact WHERE AccountId = '{account_id}'"
        contacts = self.connector.query(soql_contacts)
        
        return {
            'account': account[0] if account else {},
            'opportunities': opportunities,
            'cases': cases,
            'contacts': contacts,
            'summary': {
                'total_opportunities': len(opportunities),
                'total_cases': len(cases),
                'total_contacts': len(contacts),
                'total_opportunity_value': sum(opp.get('Amount', 0) or 0 for opp in opportunities),
                'total_claim_value': sum(case.get('Claim_Amount__c', 0) or 0 for case in cases)
            }
        }
    
    def export_for_analytics(self, object_type: str = 'Account', 
                            limit: int = 10000) -> pd.DataFrame:
        """
        Export Salesforce data for analytics (e.g., to Microsoft Fabric).
        
        Args:
            object_type: Salesforce object type to export
            limit: Maximum number of records
            
        Returns:
            DataFrame with exported data
        """
        # Build SOQL query based on object type
        if object_type == 'Account':
            soql = f"""
            SELECT Id, Name, Policy_ID__c, Policy_Type__c, Annual_Premium__c,
                   Policy_Status__c, Issue_Date__c, BillingState, Type,
                   CreatedDate, LastModifiedDate
            FROM Account
            LIMIT {limit}
            """
        elif object_type == 'Opportunity':
            soql = f"""
            SELECT Id, Name, AccountId, StageName, Amount, CloseDate,
                   Type, Probability, CreatedDate, LastModifiedDate
            FROM Opportunity
            LIMIT {limit}
            """
        elif object_type == 'Case':
            soql = f"""
            SELECT Id, Subject, AccountId, Status, Priority, Claim_ID__c,
                   Claim_Amount__c, Claim_Type__c, CreatedDate, LastModifiedDate
            FROM Case
            LIMIT {limit}
            """
        else:
            raise ValueError(f"Unsupported object type: {object_type}")
        
        records = self.connector.query(soql)
        df = pd.DataFrame(records)
        
        return df
    
    def sync_to_fabric(self, object_type: str = 'Account', 
                      fabric_workspace_id: str = None) -> Dict:
        """
        Sync Salesforce data to Microsoft Fabric for analytics.
        
        Args:
            object_type: Salesforce object type to sync
            fabric_workspace_id: Fabric workspace ID (if available)
            
        Returns:
            Dictionary with sync results
        """
        # Export data from Salesforce
        df = self.export_for_analytics(object_type)
        
        # In a real implementation, this would:
        # 1. Transform data to match Fabric schema
        # 2. Write to Fabric Lakehouse
        # 3. Update semantic models
        # 4. Refresh Power BI datasets
        
        return {
            'records_exported': len(df),
            'object_type': object_type,
            'export_timestamp': datetime.now().isoformat(),
            'data_preview': df.head().to_dict('records'),
            'note': 'In production, this would sync to Fabric Lakehouse'
        }

